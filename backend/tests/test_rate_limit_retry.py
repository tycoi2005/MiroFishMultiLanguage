"""
Unit tests for LLM rate-limit and request-too-large retry logic.

Run with:
    cd backend && uv run pytest tests/test_rate_limit_retry.py -v
"""

import pytest
from app.utils.llm_client import (
    _parse_retry_after,
    _is_request_too_large_error,
    _truncate_messages,
)


class TestParseRetryAfter:
    """Test parsing retry-after durations from error messages."""

    def test_hours_minutes_seconds(self):
        msg = "Please try again in 2h45m31.68s"
        result = _parse_retry_after(msg)
        # 2*3600 + 45*60 + 31.68 = 9931.68 -> int(9931.68) + 1 = 9932
        assert result == 9932

    def test_minutes_seconds(self):
        msg = "Please try again in 46m35.039999999s"
        result = _parse_retry_after(msg)
        # 46*60 + 35.04 = 2795.04 -> 2796
        assert result == 2796

    def test_seconds_only(self):
        msg = "Please try again in 30.5s"
        result = _parse_retry_after(msg)
        # int(30.5) + 1 = 31
        assert result == 31

    def test_minutes_only(self):
        msg = "Please try again in 5m"
        result = _parse_retry_after(msg)
        # 5*60 = 300 -> 301
        assert result == 301

    def test_hours_only(self):
        msg = "Please try again in 1h"
        result = _parse_retry_after(msg)
        assert result == 3601

    def test_full_groq_error_message(self):
        msg = (
            "Error code: 429 - {'error': {'message': 'Rate limit reached for model "
            "`llama-3.3-70b-versatile` in organization `org_01kktbv55def38ccnefrj650pv` "
            "service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99999, "
            "Requested 3502. Please try again in 50m24.864s. Need more tokens? "
            "Upgrade to Dev Tier today at https://console.groq.com/settings/billing', "
            "'type': 'tokens', 'code': 'rate_limit_exceeded'}}"
        )
        result = _parse_retry_after(msg)
        # 50*60 + 24.864 = 3024.864 -> int(3024.864) + 1 = 3025
        assert result == 3025

    def test_no_retry_info_returns_none(self):
        msg = "Some random error with no retry info"
        result = _parse_retry_after(msg)
        assert result is None

    def test_zero_seconds(self):
        msg = "Please try again in 0s"
        result = _parse_retry_after(msg)
        assert result == 1  # 0 + 1 safety margin


class TestLLMClientRetryConfig:
    """Test LLMClient retry configuration."""

    def test_default_max_retries(self):
        from app.utils.llm_client import DEFAULT_MAX_RETRIES

        assert DEFAULT_MAX_RETRIES == 3

    def test_default_max_wait(self):
        from app.utils.llm_client import DEFAULT_MAX_WAIT_SECONDS

        assert DEFAULT_MAX_WAIT_SECONDS == 15 * 60

    def test_client_stores_retry_config(self):
        from app.utils.llm_client import LLMClient

        client = LLMClient(max_retries=5, max_wait_seconds=600)
        assert client.max_retries == 5
        assert client.max_wait_seconds == 600

    def test_client_accepts_on_rate_limit_callback(self):
        from app.utils.llm_client import LLMClient

        callback_calls = []

        def my_callback(**kwargs):
            callback_calls.append(kwargs)

        client = LLMClient(on_rate_limit=my_callback)
        assert client.on_rate_limit is my_callback

    def test_client_on_rate_limit_can_be_set_after_init(self):
        from app.utils.llm_client import LLMClient

        client = LLMClient()
        assert client.on_rate_limit is None

        def my_callback(**kwargs):
            pass

        client.on_rate_limit = my_callback
        assert client.on_rate_limit is my_callback


class TestReportAgentRateLimitCallback:
    """Test that ReportAgent wires the rate-limit callback."""

    def test_report_agent_sets_on_rate_limit(self):
        from app.services.report_agent import ReportAgent

        agent = ReportAgent(
            graph_id="g1", simulation_id="s1", simulation_requirement="test"
        )
        assert agent.llm.on_rate_limit is not None
        assert callable(agent.llm.on_rate_limit)

    def test_rate_limit_callback_is_bound_to_agent(self):
        from app.services.report_agent import ReportAgent

        agent = ReportAgent(
            graph_id="g1", simulation_id="s1", simulation_requirement="test"
        )
        # The callback should be the agent's _on_rate_limit method
        cb = agent.llm.on_rate_limit
        assert hasattr(cb, "__func__")
        assert cb.__func__.__name__ == "_on_rate_limit"


class TestRequestTooLargeDetection:
    """Test detection of 413 / request-too-large errors."""

    def test_groq_413_as_rate_limit(self):
        """Groq sends 413 as a rate limit error with 'reduce your message size'."""
        msg = (
            "Error code: 413 - {'error': {'message': 'Request too large for model "
            "llama-3.3-70b-versatile in organization org_01 service tier on_demand "
            "on tokens per minute (TPM): Limit 12000, Requested 12070, please "
            "reduce your message size and try again.'}}"
        )
        # Create a fake exception
        err = Exception(msg)
        assert _is_request_too_large_error(err)

    def test_plain_413(self):
        err = Exception("Error code: 413 - request too large")
        assert _is_request_too_large_error(err)

    def test_normal_429_not_detected_as_413(self):
        err = Exception(
            "Error code: 429 - Rate limit reached for model. "
            "Please try again in 50m24s."
        )
        assert not _is_request_too_large_error(err)

    def test_unrelated_error_not_detected(self):
        err = Exception("Connection refused")
        assert not _is_request_too_large_error(err)


class TestTruncateMessages:
    """Test the message truncation helper."""

    def test_truncates_longest_message(self):
        messages = [
            {"role": "system", "content": "You are a helper."},
            {"role": "user", "content": "A" * 1000},
            {"role": "assistant", "content": "B" * 5000},
            {"role": "user", "content": "C" * 200},
        ]
        result = _truncate_messages(messages, reduction_ratio=0.5)
        # The assistant message (5000 chars) should be truncated
        assert len(result[2]["content"]) < 5000
        # System message untouched
        assert result[0]["content"] == "You are a helper."
        # Other messages untouched
        assert result[1]["content"] == "A" * 1000
        assert result[3]["content"] == "C" * 200

    def test_never_truncates_system_message(self):
        messages = [
            {"role": "system", "content": "X" * 10000},
            {"role": "user", "content": "short"},
        ]
        result = _truncate_messages(messages, reduction_ratio=0.5)
        # System message should be untouched, user message too short to truncate
        assert result[0]["content"] == "X" * 10000

    def test_returns_new_list(self):
        messages = [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "A" * 500},
        ]
        result = _truncate_messages(messages)
        assert result is not messages
        # Original should not be modified
        assert len(messages[1]["content"]) == 500

    def test_adds_truncation_note(self):
        messages = [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "A" * 2000},
        ]
        result = _truncate_messages(messages, reduction_ratio=0.5)
        assert "truncated" in result[1]["content"].lower()
        assert "1000" in result[1]["content"]  # new length ~1000

    def test_single_message_returns_as_is(self):
        messages = [{"role": "system", "content": "only one"}]
        result = _truncate_messages(messages)
        assert result == messages

    def test_short_messages_not_truncated(self):
        messages = [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "short msg"},
        ]
        result = _truncate_messages(messages)
        assert result[1]["content"] == "short msg"
