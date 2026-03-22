"""
API Health Check endpoint.
Tests LLM and Zep API connectivity, reports status and rate limits.
"""

import time
import logging
from flask import Blueprint, jsonify
from ..config import Config

logger = logging.getLogger(__name__)
health_bp = Blueprint("health", __name__)


def _check_llm_api():
    """Check LLM API health by sending a minimal request."""
    result = {
        "name": "LLM API",
        "configured": bool(Config.LLM_API_KEY),
        "base_url": Config.LLM_BASE_URL or "Not set",
        "model": Config.LLM_MODEL_NAME or "Not set",
        "status": "unknown",
        "latency_ms": None,
        "error": None,
        "rate_limit": None,
    }

    if not Config.LLM_API_KEY:
        result["status"] = "not_configured"
        result["error"] = "LLM_API_KEY is not set"
        return result

    try:
        from openai import (
            OpenAI,
            RateLimitError,
            AuthenticationError,
            APIConnectionError,
        )

        client = OpenAI(api_key=Config.LLM_API_KEY, base_url=Config.LLM_BASE_URL)

        start = time.time()
        raw = client.chat.completions.with_raw_response.create(
            model=Config.LLM_MODEL_NAME,
            messages=[{"role": "user", "content": "Say OK"}],
            max_tokens=3,
            temperature=0,
        )
        latency = int((time.time() - start) * 1000)

        result["status"] = "healthy"
        result["latency_ms"] = latency

        # Extract rate limit info from response headers
        try:
            headers = raw.headers
            rate_info = {}
            for header in [
                "x-ratelimit-limit-requests",
                "x-ratelimit-limit-tokens",
                "x-ratelimit-remaining-requests",
                "x-ratelimit-remaining-tokens",
                "x-ratelimit-reset-requests",
                "x-ratelimit-reset-tokens",
            ]:
                val = headers.get(header)
                if val is not None:
                    key = header.replace("x-ratelimit-", "").replace("-", "_")
                    rate_info[key] = val
            if rate_info:
                result["rate_limit"] = rate_info
        except Exception:
            pass

    except RateLimitError as e:
        result["status"] = "rate_limited"
        result["error"] = str(e)
        # Parse remaining wait time
        from ..utils.llm_client import _parse_retry_after

        wait = _parse_retry_after(str(e))
        if wait:
            result["rate_limit"] = {"retry_after_seconds": wait}

    except AuthenticationError as e:
        result["status"] = "auth_error"
        result["error"] = f"Authentication failed: {str(e)}"

    except APIConnectionError as e:
        result["status"] = "connection_error"
        result["error"] = f"Cannot connect to {Config.LLM_BASE_URL}: {str(e)}"

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


def _check_zep_api():
    """Check Zep API health."""
    result = {
        "name": "Zep Cloud",
        "configured": bool(Config.ZEP_API_KEY),
        "status": "unknown",
        "latency_ms": None,
        "error": None,
    }

    if not Config.ZEP_API_KEY:
        result["status"] = "not_configured"
        result["error"] = "ZEP_API_KEY is not set"
        return result

    try:
        from zep_cloud.client import Zep

        start = time.time()
        client = Zep(api_key=Config.ZEP_API_KEY)
        # Simple connectivity test — list graphs (lightweight)
        client.graph.list_all()
        latency = int((time.time() - start) * 1000)

        result["status"] = "healthy"
        result["latency_ms"] = latency

    except Exception as e:
        error_str = str(e)
        if "401" in error_str or "unauthorized" in error_str.lower():
            result["status"] = "auth_error"
            result["error"] = "Authentication failed — check ZEP_API_KEY"
        elif "connection" in error_str.lower() or "timeout" in error_str.lower():
            result["status"] = "connection_error"
            result["error"] = f"Cannot connect to Zep Cloud: {error_str}"
        else:
            result["status"] = "error"
            result["error"] = error_str

    return result


@health_bp.route("/check", methods=["GET"])
def api_health_check():
    """
    Full API health check.
    Returns status of LLM API and Zep API including rate limits.
    """
    llm_result = _check_llm_api()
    zep_result = _check_zep_api()

    all_healthy = (
        llm_result["status"] == "healthy" and zep_result["status"] == "healthy"
    )

    return jsonify(
        {
            "overall_status": "healthy" if all_healthy else "degraded",
            "services": [llm_result, zep_result],
            "config": {
                "llm_model": Config.LLM_MODEL_NAME,
                "llm_base_url": Config.LLM_BASE_URL,
                "max_retries": 3,
                "max_wait_seconds": 900,
            },
        }
    )
