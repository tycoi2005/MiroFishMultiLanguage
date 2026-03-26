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
    """Check LLM API health using the provider registry.

    Tests the next round-robin client and returns per-provider status.
    """
    from app.utils.llm_registry import get_registry

    registry = get_registry()

    if registry.provider_count == 0:
        return {
            "name": "LLM API",
            "configured": False,
            "status": "not_configured",
            "error": "No LLM providers configured",
            "providers": [],
        }

    from openai import (
        OpenAI,
        RateLimitError,
        AuthenticationError,
        APIConnectionError,
    )
    from ..utils.llm_client import _parse_retry_after

    # Test each provider individually
    providers_status = []
    overall_healthy = False

    for pconfig in registry.providers:
        pstatus = {
            "name": pconfig.name,
            "base_url": pconfig.base_url,
            "model": pconfig.model,
            "is_local": pconfig.is_local,
            "status": "unknown",
            "latency_ms": None,
            "error": None,
            "rate_limit": None,
        }

        try:
            api_key = pconfig.api_key
            if pconfig.is_local and not api_key:
                api_key = "local"

            client = OpenAI(api_key=api_key, base_url=pconfig.base_url)

            start = time.time()
            raw = client.chat.completions.with_raw_response.create(
                model=pconfig.model,
                messages=[{"role": "user", "content": "Say OK"}],
                max_tokens=3,
                temperature=0,
            )
            latency = int((time.time() - start) * 1000)

            pstatus["status"] = "healthy"
            pstatus["latency_ms"] = latency
            overall_healthy = True

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
                    pstatus["rate_limit"] = rate_info
            except Exception:
                pass

        except RateLimitError as e:
            pstatus["status"] = "rate_limited"
            pstatus["error"] = str(e)
            wait = _parse_retry_after(str(e))
            if wait:
                pstatus["rate_limit"] = {"retry_after_seconds": wait}

        except AuthenticationError as e:
            pstatus["status"] = "auth_error"
            pstatus["error"] = f"Authentication failed: {str(e)}"

        except APIConnectionError as e:
            pstatus["status"] = "connection_error"
            pstatus["error"] = f"Cannot connect to {pconfig.base_url}: {str(e)}"

        except Exception as e:
            pstatus["status"] = "error"
            pstatus["error"] = str(e)

        providers_status.append(pstatus)

    # Build the summary result (backwards compatible)
    first_healthy = next(
        (p for p in providers_status if p["status"] == "healthy"), None
    )
    representative = first_healthy or providers_status[0]

    result = {
        "name": "LLM API",
        "configured": True,
        "provider_count": registry.provider_count,
        "base_url": representative["base_url"],
        "model": representative["model"],
        "status": "healthy" if overall_healthy else representative["status"],
        "latency_ms": representative.get("latency_ms"),
        "error": None if overall_healthy else representative.get("error"),
        "rate_limit": representative.get("rate_limit"),
        "providers": providers_status,
    }

    return result


def _list_available_models():
    """List available chat models from ALL configured providers."""
    from app.utils.llm_registry import get_registry
    from openai import OpenAI

    registry = get_registry()
    if registry.provider_count == 0:
        return []

    EXCLUDE_PREFIXES = (
        "models/imagen",
        "models/veo",
        "models/lyria",
        "models/gemini-embedding",
        "models/gemma",
        "models/nano",
        "models/gemini-robotics",
    )
    EXCLUDE_CONTAINS = (
        "tts",
        "audio",
        "image",
        "embedding",
    )

    all_models = []
    seen_ids = set()

    for pconfig in registry.providers:
        try:
            api_key = pconfig.api_key or "local"
            client = OpenAI(api_key=api_key, base_url=pconfig.base_url)
            response = client.models.list()

            for model in response.data:
                model_id = model.id
                if any(model_id.startswith(p) for p in EXCLUDE_PREFIXES):
                    continue
                if any(kw in model_id.lower() for kw in EXCLUDE_CONTAINS):
                    continue
                # Deduplicate across providers
                dedup_key = f"{pconfig.name}:{model_id}"
                if dedup_key in seen_ids:
                    continue
                seen_ids.add(dedup_key)

                all_models.append(
                    {
                        "id": model_id,
                        "provider": pconfig.name,
                        "owned_by": getattr(model, "owned_by", None),
                    }
                )
        except Exception as e:
            logger.warning(f"Failed to list models from {pconfig.name}: {str(e)[:100]}")
            all_models.append(
                {
                    "provider": pconfig.name,
                    "error": f"Cannot list models: {str(e)[:100]}",
                }
            )

    all_models.sort(key=lambda m: (m.get("provider", ""), m.get("id", "")))
    return all_models


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
    from app.utils.llm_registry import get_registry

    llm_result = _check_llm_api()
    zep_result = _check_zep_api()
    available_models = _list_available_models()

    registry = get_registry()
    all_healthy = (
        llm_result["status"] == "healthy" and zep_result["status"] == "healthy"
    )

    return jsonify(
        {
            "overall_status": "healthy" if all_healthy else "degraded",
            "services": [llm_result, zep_result],
            "available_models": available_models,
            "config": {
                "provider_count": registry.provider_count,
                "providers": [p.to_dict() for p in registry.providers],
                "max_retries": 3,
                "max_wait_seconds": 900,
            },
        }
    )
