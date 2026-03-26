"""
Unit tests for LLM provider registry and round-robin load balancing.

Run with:
    cd backend && uv run pytest tests/test_llm_registry.py -v
"""

import os
import time
import pytest
from unittest.mock import patch
from app.utils.llm_registry import (
    LLMProviderRegistry,
    ProviderConfig,
    get_registry,
    reset_registry,
)


@pytest.fixture(autouse=True)
def cleanup_registry():
    """Reset the singleton registry before each test."""
    reset_registry()
    yield
    reset_registry()


class TestProviderConfig:
    """Test ProviderConfig dataclass."""

    def test_basic_config(self):
        config = ProviderConfig(
            name="test",
            api_key="key123",
            base_url="https://api.example.com/v1",
            model="test-model",
        )
        assert config.name == "test"
        assert config.is_local == False

    def test_local_config(self):
        config = ProviderConfig(
            name="ollama",
            api_key="ollama",
            base_url="http://localhost:11434/v1",
            model="qwen3:8b",
            is_local=True,
        )
        assert config.is_local == True

    def test_to_dict_hides_api_key(self):
        config = ProviderConfig(
            name="test",
            api_key="secret_key_123",
            base_url="https://api.example.com/v1",
            model="test-model",
        )
        d = config.to_dict()
        assert "api_key" not in d
        assert d["name"] == "test"
        assert d["model"] == "test-model"


class TestRegistryLoading:
    """Test provider loading from environment variables."""

    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDERS": '[{"name":"p1","api_key":"k1","base_url":"http://a.com/v1","model":"m1"},{"name":"p2","api_key":"k2","base_url":"http://b.com/v1","model":"m2"}]',
        },
        clear=False,
    )
    def test_load_from_json_env(self):
        reg = LLMProviderRegistry()
        assert reg.provider_count == 2
        assert reg.providers[0].name == "p1"
        assert reg.providers[1].name == "p2"

    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDER_1_NAME": "test1",
            "LLM_PROVIDER_1_API_KEY": "key1",
            "LLM_PROVIDER_1_BASE_URL": "http://test1.com/v1",
            "LLM_PROVIDER_1_MODEL": "model1",
            "LLM_PROVIDER_2_NAME": "test2",
            "LLM_PROVIDER_2_API_KEY": "key2",
            "LLM_PROVIDER_2_BASE_URL": "http://test2.com/v1",
            "LLM_PROVIDER_2_MODEL": "model2",
            "LLM_PROVIDER_2_LOCAL": "true",
        },
        clear=False,
    )
    def test_load_from_numbered_env(self):
        # Clear LLM_PROVIDERS to force numbered loading
        with patch.dict(os.environ, {"LLM_PROVIDERS": ""}, clear=False):
            reg = LLMProviderRegistry()
            assert reg.provider_count >= 2
            names = [p.name for p in reg.providers]
            assert "test1" in names
            assert "test2" in names
            # test2 should be local
            test2 = reg.get_provider_config("test2")
            assert test2 is not None
            assert test2.is_local == True

    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDERS": '[{"name":"groq","api_key":"k1","base_url":"http://a.com/v1","model":"m1"},{"name":"groq","api_key":"k2","base_url":"http://b.com/v1","model":"m2"},{"name":"groq","api_key":"k3","base_url":"http://c.com/v1","model":"m3"}]',
        },
        clear=False,
    )
    def test_auto_dedup_duplicate_names(self):
        """Providers with the same name get auto-suffixed."""
        reg = LLMProviderRegistry()
        names = [p.name for p in reg.providers]
        assert "groq" in names
        assert "groq-2" in names
        assert "groq-3" in names
        assert len(set(names)) == len(names)  # all unique

    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDERS": '[{"name":"a","api_key":"k","base_url":"http://a.com/v1","model":"m"},]',
        },
        clear=False,
    )
    def test_trailing_comma_in_json(self):
        """Trailing comma in JSON array should be handled."""
        reg = LLMProviderRegistry()
        assert reg.provider_count >= 1
        assert reg.providers[0].name == "a"

    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDERS": "",
            "LLM_API_KEY": "test-legacy-key",
            "LLM_BASE_URL": "http://legacy.com/v1",
            "LLM_MODEL_NAME": "legacy-model",
        },
        clear=False,
    )
    def test_legacy_fallback(self):
        """When no LLM_PROVIDERS set, falls back to Config.LLM_API_KEY."""
        reg = LLMProviderRegistry()
        assert reg.provider_count >= 1
        assert reg.providers[0].name == "default"

    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDERS": '[{"name":"local","api_key":"ollama","base_url":"http://localhost:11434/v1","model":"qwen3:8b","is_local":true}]',
        },
        clear=False,
    )
    def test_local_provider(self):
        reg = LLMProviderRegistry()
        assert reg.provider_count >= 1
        local = reg.get_provider_config("local")
        assert local is not None
        assert local.is_local == True


class TestRoundRobin:
    """Test round-robin client selection."""

    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDERS": '[{"name":"a","api_key":"ka","base_url":"http://a.com/v1","model":"ma"},{"name":"b","api_key":"kb","base_url":"http://b.com/v1","model":"mb"},{"name":"c","api_key":"kc","base_url":"http://c.com/v1","model":"mc"}]',
        },
        clear=False,
    )
    def test_round_robin_cycles(self):
        reg = LLMProviderRegistry()
        # Get clients in sequence — should cycle through a, b, c, a, b, c
        models = []
        for _ in range(6):
            client = reg.next_client()
            models.append(client.model)
        assert models == ["ma", "mb", "mc", "ma", "mb", "mc"]

    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDERS": '[{"name":"a","api_key":"ka","base_url":"http://a.com/v1","model":"ma"},{"name":"b","api_key":"kb","base_url":"http://b.com/v1","model":"mb"}]',
        },
        clear=False,
    )
    def test_skips_rate_limited_provider(self):
        reg = LLMProviderRegistry()
        # Mark 'a' as rate limited
        reg.mark_rate_limited("a", cooldown_seconds=60)
        # Next 3 calls should all return 'b'
        for _ in range(3):
            client = reg.next_client()
            assert client.model == "mb"

    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDERS": '[{"name":"a","api_key":"ka","base_url":"http://a.com/v1","model":"ma"},{"name":"b","api_key":"kb","base_url":"http://b.com/v1","model":"mb"}]',
        },
        clear=False,
    )
    def test_rate_limit_expires(self):
        reg = LLMProviderRegistry()
        # Mark 'a' as rate limited for 1 second
        reg.mark_rate_limited("a", cooldown_seconds=1)
        time.sleep(1.5)
        # Now 'a' should be available again
        # Reset index to start from 'a'
        reg._index = 0
        client = reg.next_client()
        assert client.model == "ma"

    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDERS": '[{"name":"a","api_key":"ka","base_url":"http://a.com/v1","model":"ma"},{"name":"b","api_key":"kb","base_url":"http://b.com/v1","model":"mb"}]',
        },
        clear=False,
    )
    def test_all_rate_limited_returns_soonest(self):
        reg = LLMProviderRegistry()
        reg.mark_rate_limited("a", cooldown_seconds=100)
        reg.mark_rate_limited("b", cooldown_seconds=10)
        # Should return 'b' (expires sooner)
        client = reg.next_client()
        assert client.model == "mb"

    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDERS": '[{"name":"solo","api_key":"k","base_url":"http://s.com/v1","model":"ms"}]',
        },
        clear=False,
    )
    def test_single_provider_round_robin(self):
        reg = LLMProviderRegistry()
        for _ in range(5):
            client = reg.next_client()
            assert client.model == "ms"


class TestGetClient:
    """Test getting specific providers by name."""

    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDERS": '[{"name":"gemini","api_key":"k1","base_url":"http://g.com/v1","model":"gemini-2.5"},{"name":"groq","api_key":"k2","base_url":"http://q.com/v1","model":"llama-70b"}]',
        },
        clear=False,
    )
    def test_get_by_name(self):
        reg = LLMProviderRegistry()
        client = reg.get_client("groq")
        assert client is not None
        assert client.model == "llama-70b"

    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDERS": '[{"name":"a","api_key":"k","base_url":"http://a.com/v1","model":"m"}]',
        },
        clear=False,
    )
    def test_get_nonexistent_returns_none(self):
        reg = LLMProviderRegistry()
        assert reg.get_client("nonexistent") is None

    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDERS": '[{"name":"a","api_key":"k","base_url":"http://a.com/v1","model":"m"}]',
        },
        clear=False,
    )
    def test_same_client_instance_reused(self):
        reg = LLMProviderRegistry()
        c1 = reg.get_client("a")
        c2 = reg.get_client("a")
        assert c1 is c2  # Same instance, not recreated


class TestNextClientWithName:
    """Test next_client_with_name() returns both client and provider name."""

    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDERS": '[{"name":"alpha","api_key":"k","base_url":"http://a.com/v1","model":"m1"},{"name":"beta","api_key":"k","base_url":"http://b.com/v1","model":"m2"}]',
        },
        clear=False,
    )
    def test_returns_tuple(self):
        reg = LLMProviderRegistry()
        client, name = reg.next_client_with_name()
        assert client is not None
        assert name in ("alpha", "beta")

    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDERS": '[{"name":"alpha","api_key":"k","base_url":"http://a.com/v1","model":"m1"},{"name":"beta","api_key":"k","base_url":"http://b.com/v1","model":"m2"}]',
        },
        clear=False,
    )
    def test_cycles_names(self):
        reg = LLMProviderRegistry()
        names = []
        for _ in range(4):
            _, name = reg.next_client_with_name()
            names.append(name)
        assert names == ["alpha", "beta", "alpha", "beta"]


class TestSingleton:
    """Test the global singleton registry."""

    def test_get_registry_returns_same_instance(self):
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2

    def test_reset_clears_singleton(self):
        r1 = get_registry()
        reset_registry()
        r2 = get_registry()
        assert r1 is not r2
