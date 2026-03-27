"""
LLM client wrapper.
Unified OpenAI-format API calls with automatic retry for:
  - 429 Rate Limit: wait and retry
  - 413 Request Too Large: truncate messages and retry
"""

import json
import logging
import re
import threading
import time
from typing import Optional, Dict, Any, List

from openai import OpenAI, RateLimitError, BadRequestError

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


def _is_request_too_large_error(error: Exception) -> bool:
    """Check if an error is a 413/request-too-large error (including Groq's 413-as-rate-limit)."""
    msg = str(error).lower()
    return (
        "413" in msg
        or "request too large" in msg
        or ("rate_limit" in msg and "reduce your message size" in msg)
    )


def _truncate_messages(
    messages: List[Dict[str, str]], reduction_ratio: float = 0.6
) -> List[Dict[str, str]]:
    """
    Truncate the longest user/assistant message to reduce total token count.

    Strategy:
    1. Never touch the system message (index 0)
    2. Find the longest non-system message by character count
    3. Truncate it to reduction_ratio of its current length
    4. Add a note that content was truncated

    Returns a new list (does not modify the original).
    """
    if len(messages) <= 1:
        return messages

    result = [m.copy() for m in messages]

    # Find the longest non-system message
    max_len = 0
    max_idx = -1
    for i, m in enumerate(result):
        if m.get("role") == "system":
            continue
        content = m.get("content", "")
        if len(content) > max_len:
            max_len = len(content)
            max_idx = i

    if max_idx < 0 or max_len < 200:
        return result  # Nothing useful to truncate

    content = result[max_idx]["content"]
    new_len = int(len(content) * reduction_ratio)
    result[max_idx] = result[max_idx].copy()
    result[max_idx]["content"] = (
        content[:new_len]
        + f"\n\n... [Content truncated from {len(content)} to {new_len} chars to fit model context limit]"
    )

    logger.info(
        f"Truncated message at index {max_idx} from {len(content)} to {new_len} chars"
    )
    return result


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

        # Event to skip the current sleep (set by "Retry Now" button)
        self._skip_wait = threading.Event()

        # Local providers (Ollama, LM Studio) use placeholder keys
        if not self.api_key or self.api_key in ("ollama", "local", "none", "lm-studio"):
            self.api_key = self.api_key or "local"

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None,
    ) -> str:
        """
        Send a chat request with automatic retry:
          - 429 Rate Limit: parse retry-after, wait, retry
          - 413 Request Too Large: truncate longest message, retry immediately
        """
        current_messages = list(messages)

        kwargs = {
            "model": self.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format:
            kwargs["response_format"] = response_format

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                kwargs["messages"] = current_messages
                response = self.client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content
                # Some models include <think> tags — strip them
                content = re.sub(r"<think>[\s\S]*?</think>", "", content).strip()
                return content

            except RateLimitError as e:
                last_error = e
                error_msg = str(e)

                # Check if this is actually a 413 "request too large" disguised as rate limit
                if _is_request_too_large_error(e):
                    logger.warning(
                        f"Request too large (413). Attempt {attempt}/{self.max_retries}. "
                        f"Truncating messages and retrying..."
                    )
                    current_messages = _truncate_messages(current_messages)

                    if self.on_rate_limit:
                        try:
                            self.on_rate_limit(
                                wait_seconds=5,
                                attempt=attempt,
                                max_retries=self.max_retries,
                                error_msg="Request too large — auto-truncating and retrying...",
                            )
                        except Exception:
                            pass
                    time.sleep(2)  # Brief pause before retry
                    continue

                # Normal 429 rate limit
                wait_seconds = _parse_retry_after(error_msg)
                if wait_seconds is None or wait_seconds <= 0:
                    wait_seconds = min(60 * (2 ** (attempt - 1)), self.max_wait_seconds)
                wait_seconds = min(wait_seconds, self.max_wait_seconds)

                # If max_retries=1, raise immediately (let the balancer handle failover)
                if self.max_retries <= 1:
                    raise

                wait_minutes = round(wait_seconds / 60, 1)
                logger.warning(
                    f"Rate limited (429). Attempt {attempt}/{self.max_retries}. "
                    f"Waiting {wait_minutes} min before retry..."
                )

                if self.on_rate_limit:
                    try:
                        self.on_rate_limit(
                            wait_seconds=wait_seconds,
                            attempt=attempt,
                            max_retries=self.max_retries,
                            error_msg=error_msg,
                        )
                    except Exception:
                        pass

                # Interruptible sleep — can be skipped by calling skip_wait()
                self._skip_wait.clear()
                skipped = self._skip_wait.wait(timeout=wait_seconds)
                if skipped:
                    logger.info("Wait skipped by manual retry request")

            except BadRequestError as e:
                # Some providers return 413 as a BadRequestError
                if _is_request_too_large_error(e):
                    last_error = e
                    logger.warning(
                        f"Request too large (BadRequest/413). Attempt {attempt}/{self.max_retries}. "
                        f"Truncating messages and retrying..."
                    )
                    current_messages = _truncate_messages(current_messages)
                    time.sleep(2)
                    continue
                raise  # Re-raise non-size-related bad requests

        # All retries exhausted
        raise last_error

    def skip_wait(self):
        """Skip the current rate-limit sleep. Called by 'Retry Now' button."""
        self._skip_wait.set()

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 8192,
    ) -> Dict[str, Any]:
        """
        Send a chat request and return parsed JSON.
        Retries with higher max_tokens if response is truncated.
        Attempts to repair truncated JSON before giving up.
        """
        last_error = None
        # Try with increasing max_tokens if JSON is truncated
        for attempt_tokens in [max_tokens, max_tokens * 2, max_tokens * 3]:
            response = self.chat(
                messages=messages,
                temperature=temperature,
                max_tokens=attempt_tokens,
                response_format={"type": "json_object"},
            )
            # Clean markdown code block markers
            cleaned = response.strip()
            cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\n?```\s*$", "", cleaned)
            cleaned = cleaned.strip()

            try:
                return json.loads(cleaned)
            except json.JSONDecodeError as e:
                last_error = e
                logger.warning(
                    f"JSON parse failed (max_tokens={attempt_tokens}): {str(e)[:100]}"
                )

                # Try to repair truncated JSON
                repaired = self._try_repair_json(cleaned)
                if repaired is not None:
                    logger.info("Successfully repaired truncated JSON")
                    return repaired

                # If the response looks truncated (ends mid-string/mid-object),
                # retry with more tokens
                if attempt_tokens < max_tokens * 3:
                    logger.info(
                        f"Retrying with higher max_tokens: {attempt_tokens * 2}"
                    )
                    continue

        raise ValueError(f"Invalid JSON from LLM after retries: {str(last_error)}")

    @staticmethod
    def _try_repair_json(text: str) -> Optional[Dict]:
        """
        Attempt to repair truncated JSON by closing open brackets/braces.
        Returns parsed dict if successful, None if not.
        """
        if not text or not text.startswith("{"):
            return None

        # Count open/close brackets
        open_braces = text.count("{") - text.count("}")
        open_brackets = text.count("[") - text.count("]")

        if open_braces <= 0 and open_brackets <= 0:
            return None  # Not a truncation issue

        # Try progressively aggressive truncation + closure
        # Strategy: find the last complete item, close everything
        repaired = text.rstrip().rstrip(",")

        # If we're inside a string, close it
        in_string = False
        escaped = False
        for ch in repaired:
            if escaped:
                escaped = False
                continue
            if ch == "\\":
                escaped = True
                continue
            if ch == '"':
                in_string = not in_string

        if in_string:
            repaired += '"'

        # Close remaining brackets and braces
        for _ in range(open_brackets):
            repaired += "]"
        for _ in range(open_braces):
            repaired += "}"

        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            # More aggressive: strip back to last complete object/array element
            # Find last valid closing point
            for i in range(len(text) - 1, max(0, len(text) - 500), -1):
                if text[i] in ("}", "]"):
                    snippet = text[: i + 1]
                    # Close any remaining open structures
                    ob = snippet.count("{") - snippet.count("}")
                    ol = snippet.count("[") - snippet.count("]")
                    snippet += "]" * max(0, ol) + "}" * max(0, ob)
                    try:
                        return json.loads(snippet)
                    except json.JSONDecodeError:
                        continue

        return None


class LLMBalancer:
    """
    Drop-in replacement for LLMClient that rotates across all providers
    on EVERY call via round-robin. On 429, marks the provider as rate-limited
    and immediately tries the next one instead of sleeping.

    Usage:
        balancer = LLMBalancer()
        result = balancer.chat(messages)       # uses provider 1
        result = balancer.chat(messages)       # uses provider 2 (round-robin)
        # if provider 2 hits 429 -> mark it, try provider 3 instantly
    """

    def __init__(self, on_rate_limit=None):
        self.on_rate_limit = on_rate_limit
        self._skip_wait = threading.Event()
        from .llm_registry import get_registry

        reg = get_registry()
        self.model = reg.providers[0].model if reg.providers else "unknown"

    def _call_with_failover(self, method_name, **kwargs):
        """
        Try the next provider. On 429, mark it rate-limited and try the next one.
        Only sleep if ALL providers are exhausted.
        """
        from .llm_registry import get_registry

        registry = get_registry()
        n = registry.provider_count
        if n == 0:
            raise RuntimeError("No LLM providers configured")

        last_error = None

        # Try each provider once before giving up
        for attempt in range(n):
            client, name = registry.next_client_with_name()
            if self.on_rate_limit:
                client.on_rate_limit = self.on_rate_limit
            client._skip_wait = self._skip_wait
            # Set max_retries=1 on the client so it doesn't sleep on 429
            # — we handle failover at the balancer level instead
            old_retries = client.max_retries
            client.max_retries = 1

            try:
                result = getattr(client, method_name)(**kwargs)
                client.max_retries = old_retries
                return result
            except RateLimitError as e:
                client.max_retries = old_retries
                last_error = e
                error_msg = str(e)

                # For 413 (request too large), also try next provider — it may
                # have a higher TPM limit (e.g., local Ollama vs cloud Groq 12K)
                if _is_request_too_large_error(e):
                    logger.warning(
                        f"Provider '{name}' request too large. Trying next provider..."
                    )
                    # Don't mark as rate-limited — it's a size issue, not a quota issue
                    continue

                # Mark this provider as rate-limited
                wait_seconds = _parse_retry_after(error_msg) or 60
                registry.mark_rate_limited(name, wait_seconds)
                logger.warning(
                    f"Provider '{name}' rate-limited. Trying next provider... "
                    f"({attempt + 1}/{n} tried)"
                )

                if self.on_rate_limit:
                    try:
                        self.on_rate_limit(
                            wait_seconds=5,
                            attempt=attempt + 1,
                            max_retries=n,
                            error_msg=f"Provider '{name}' rate-limited, switching to next...",
                        )
                    except Exception:
                        pass
                continue
            except BadRequestError as e:
                client.max_retries = old_retries
                if _is_request_too_large_error(e):
                    raise
                raise

        # All providers exhausted — fall back to the original single-client retry
        # which will sleep and wait for a provider to recover
        logger.warning("All providers rate-limited. Falling back to wait-and-retry...")
        client, name = registry.next_client_with_name()
        if self.on_rate_limit:
            client.on_rate_limit = self.on_rate_limit
        client._skip_wait = self._skip_wait
        return getattr(client, method_name)(**kwargs)

    def chat(self, messages, temperature=0.7, max_tokens=4096, response_format=None):
        return self._call_with_failover(
            "chat",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )

    def chat_json(self, messages, temperature=0.3, max_tokens=8192):
        return self._call_with_failover(
            "chat_json",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def skip_wait(self):
        self._skip_wait.set()
