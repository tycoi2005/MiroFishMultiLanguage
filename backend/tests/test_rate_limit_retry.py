"""
Unit tests for LLM rate-limit retry logic.

Run with:
    cd backend && uv run pytest tests/test_rate_limit_retry.py -v
"""

import pytest
from app.utils.llm_client import _parse_retry_after


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
