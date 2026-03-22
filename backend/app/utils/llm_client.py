"""
LLM client wrapper.
Unified OpenAI-format API calls with automatic 429 rate-limit retry.
"""

import json
import logging
import re
import time
from typing import Optional, Dict, Any, List

from openai import OpenAI, RateLimitError

from ..config import Config

logger = logging.getLogger(__name__)

# Default retry config
DEFAULT_MAX_RETRIES = 3
DEFAULT_MAX_WAIT_SECONDS = 15 * 60  # 15 minutes max wait per retry


def _parse_retry_after(error_message: str) -> Optional[int]:
    """
    Parse the suggested wait time from a Groq/OpenAI 429 error message.

    Looks for patterns like:
      "Please try again in 2h45m31.68s"
      "Please try again in 46m35.039999999s"
      "Please try again in 30.5s"

    Returns wait time in seconds, or None if unparseable.
    """
    match = re.search(
        r"try again in\s+(?:(\d+)h)?(?:(\d+)m)?(?:(\d+(?:\.\d+)?)s)?", error_message
    )
    if not match:
        return None
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = float(match.group(3) or 0)
    total = hours * 3600 + minutes * 60 + seconds
    return int(total) + 1  # +1 for safety margin


class LLMClient:
    """LLM client with automatic rate-limit retry."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        max_wait_seconds: int = DEFAULT_MAX_WAIT_SECONDS,
        on_rate_limit: Optional[Any] = None,
    ):
        """
        Args:
            on_rate_limit: Optional callback(wait_seconds, attempt, max_retries, error_msg)
                           called when a 429 is hit, before sleeping. Allows the caller
                           (e.g. ReportAgent) to log the pause to the agent log / UI.
        """
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model = model or Config.LLM_MODEL_NAME
        self.max_retries = max_retries
        self.max_wait_seconds = max_wait_seconds
        self.on_rate_limit = on_rate_limit

        if not self.api_key:
            raise ValueError("LLM_API_KEY is not configured")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None,
    ) -> str:
        """
        Send a chat request with automatic retry on 429 rate limit errors.

        Parses the retry-after time from the error message, waits, and retries
        up to max_retries times.
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format:
            kwargs["response_format"] = response_format

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content
                # Some models include <think> tags — strip them
                content = re.sub(r"<think>[\s\S]*?</think>", "", content).strip()
                return content
            except RateLimitError as e:
                last_error = e
                error_msg = str(e)

                # Parse suggested wait time from error
                wait_seconds = _parse_retry_after(error_msg)
                if wait_seconds is None or wait_seconds <= 0:
                    wait_seconds = min(60 * (2 ** (attempt - 1)), self.max_wait_seconds)

                # Cap the wait time
                wait_seconds = min(wait_seconds, self.max_wait_seconds)

                wait_minutes = round(wait_seconds / 60, 1)
                logger.warning(
                    f"Rate limited (429). Attempt {attempt}/{self.max_retries}. "
                    f"Waiting {wait_minutes} min before retry..."
                )

                # Notify caller (e.g. report agent can log to UI)
                if self.on_rate_limit:
                    try:
                        self.on_rate_limit(
                            wait_seconds=wait_seconds,
                            attempt=attempt,
                            max_retries=self.max_retries,
                            error_msg=error_msg,
                        )
                    except Exception:
                        pass  # Don't let callback errors break retry

                time.sleep(wait_seconds)

        # All retries exhausted
        raise last_error

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """
        发送聊天请求并返回JSON

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            解析后的JSON对象
        """
        response = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        # 清理markdown代码块标记
        cleaned_response = response.strip()
        cleaned_response = re.sub(
            r"^```(?:json)?\s*\n?", "", cleaned_response, flags=re.IGNORECASE
        )
        cleaned_response = re.sub(r"\n?```\s*$", "", cleaned_response)
        cleaned_response = cleaned_response.strip()

        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            raise ValueError(f"LLM返回的JSON格式无效: {cleaned_response}")
