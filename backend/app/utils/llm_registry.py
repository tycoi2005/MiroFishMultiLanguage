"""
Multi-provider LLM registry with round-robin load balancing.

Reads LLM_PROVIDERS from .env as a JSON array of provider configs,
creates LLMClient instances, and distributes calls via round-robin.

Usage:
    from app.utils.llm_registry import get_registry
    registry = get_registry()
    client = registry.next_client()   # round-robin
    client = registry.get_client("ollama")  # by name
"""

import json
import logging
import os
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .llm_client import LLMClient

logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """Configuration for a single LLM provider."""

    name: str
    api_key: str
    base_url: str
    model: str
    is_local: bool = False  # True for Ollama, LM Studio, etc.

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "base_url": self.base_url,
            "model": self.model,
            "is_local": self.is_local,
            # Never expose api_key
        }


class LLMProviderRegistry:
    """
    Manages multiple LLM providers with round-robin load balancing.

    Providers are configured via:
    1. LLM_PROVIDERS env var (JSON array) — preferred
    2. Legacy single LLM_API_KEY / LLM_BASE_URL / LLM_MODEL_NAME — fallback

    Round-robin: each call to next_client() returns the next provider
    in rotation. If a provider is rate-limited (marked via mark_rate_limited),
    it is skipped until its cooldown expires.
    """

    def __init__(self):
        self._providers: List[ProviderConfig] = []
        self._clients: Dict[str, LLMClient] = {}
        self._index = 0
        self._lock = threading.Lock()
        self._rate_limited: Dict[str, float] = {}  # name -> expiry timestamp

        self._load_providers()

    def _load_providers(self):
        """Load provider configs from environment."""
        # Try LLM_PROVIDERS JSON array first
        providers_json = os.environ.get("LLM_PROVIDERS")
        if providers_json:
            try:
                # Allow trailing commas in JSON (common user mistake)
                cleaned = providers_json.strip().rstrip(",")
                if cleaned.endswith(",]"):
                    cleaned = cleaned[:-2] + "]"
                providers_list = json.loads(cleaned)

                # Auto-deduplicate names by appending -1, -2, etc.
                name_counts: Dict[str, int] = {}
                for p in providers_list:
                    base_name = p["name"]
                    name_counts[base_name] = name_counts.get(base_name, 0) + 1
                    if name_counts[base_name] > 1:
                        unique_name = f"{base_name}-{name_counts[base_name]}"
                    else:
                        unique_name = base_name

                    config = ProviderConfig(
                        name=unique_name,
                        api_key=p.get("api_key", ""),
                        base_url=p["base_url"],
                        model=p["model"],
                        is_local=p.get("is_local", False),
                    )
                    self._providers.append(config)
                    logger.info(
                        f"Loaded LLM provider: {config.name} ({config.model} @ {config.base_url})"
                    )
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                logger.error(f"Failed to parse LLM_PROVIDERS: {e}")

        # Also check numbered LLM_PROVIDER_N_* env vars
        for i in range(1, 20):
            name = os.environ.get(f"LLM_PROVIDER_{i}_NAME")
            if not name:
                break
            config = ProviderConfig(
                name=name,
                api_key=os.environ.get(f"LLM_PROVIDER_{i}_API_KEY", ""),
                base_url=os.environ.get(f"LLM_PROVIDER_{i}_BASE_URL", ""),
                model=os.environ.get(f"LLM_PROVIDER_{i}_MODEL", ""),
                is_local=os.environ.get(f"LLM_PROVIDER_{i}_LOCAL", "").lower()
                in ("true", "1", "yes"),
            )
            # Skip duplicates
            if not any(p.name == config.name for p in self._providers):
                self._providers.append(config)
                logger.info(
                    f"Loaded LLM provider: {config.name} ({config.model} @ {config.base_url})"
                )

        # Fallback: legacy single provider from env vars
        if not self._providers:
            legacy_key = os.environ.get("LLM_API_KEY", "")
            legacy_url = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
            legacy_model = os.environ.get("LLM_MODEL_NAME", "gpt-4o-mini")

            if legacy_key:
                is_local = "localhost" in legacy_url or "127.0.0.1" in legacy_url
                config = ProviderConfig(
                    name="default",
                    api_key=legacy_key,
                    base_url=legacy_url,
                    model=legacy_model,
                    is_local=is_local,
                )
                self._providers.append(config)
                logger.info(
                    f"Loaded legacy LLM provider: {config.model} @ {config.base_url}"
                )

        if not self._providers:
            logger.warning("No LLM providers configured!")

        logger.info(f"LLM Registry: {len(self._providers)} provider(s) loaded")

    def _get_or_create_client(self, config: ProviderConfig) -> LLMClient:
        """Get or lazily create an LLMClient for a provider."""
        if config.name not in self._clients:
            api_key = config.api_key
            # Local providers (Ollama, LM Studio) don't need real API keys
            if config.is_local and not api_key:
                api_key = "local"
            self._clients[config.name] = LLMClient(
                api_key=api_key,
                base_url=config.base_url,
                model=config.model,
            )
        return self._clients[config.name]

    @property
    def providers(self) -> List[ProviderConfig]:
        """Return list of all configured providers."""
        return list(self._providers)

    @property
    def provider_count(self) -> int:
        return len(self._providers)

    def get_client(self, provider_name: str) -> Optional[LLMClient]:
        """Get a specific provider's client by name."""
        for config in self._providers:
            if config.name == provider_name:
                return self._get_or_create_client(config)
        return None

    def get_provider_config(self, provider_name: str) -> Optional[ProviderConfig]:
        """Get a provider's config by name."""
        for config in self._providers:
            if config.name == provider_name:
                return config
        return None

    def mark_rate_limited(self, provider_name: str, cooldown_seconds: int = 60):
        """Mark a provider as rate-limited for a cooldown period."""
        import time

        self._rate_limited[provider_name] = time.time() + cooldown_seconds
        logger.info(
            f"Provider '{provider_name}' marked rate-limited for {cooldown_seconds}s"
        )

    def _is_available(self, provider_name: str) -> bool:
        """Check if a provider is currently available (not rate-limited)."""
        import time

        expiry = self._rate_limited.get(provider_name)
        if expiry is None:
            return True
        if time.time() > expiry:
            del self._rate_limited[provider_name]
            return True
        return False

    def next_client(self) -> LLMClient:
        """
        Get the next available LLMClient via round-robin.
        Skips rate-limited providers. If all are rate-limited,
        returns the one with the shortest remaining cooldown.
        """
        if not self._providers:
            raise RuntimeError("No LLM providers configured")

        with self._lock:
            n = len(self._providers)

            # Try round-robin, skipping rate-limited providers
            for _ in range(n):
                config = self._providers[self._index % n]
                self._index = (self._index + 1) % n
                if self._is_available(config.name):
                    return self._get_or_create_client(config)

            # All rate-limited — pick the one expiring soonest
            import time

            soonest = min(
                self._providers, key=lambda p: self._rate_limited.get(p.name, 0)
            )
            logger.warning(
                f"All providers rate-limited. Using '{soonest.name}' (expires soonest)"
            )
            return self._get_or_create_client(soonest)

    def next_client_with_name(self) -> tuple:
        """Like next_client() but also returns the provider name. Returns (client, name)."""
        if not self._providers:
            raise RuntimeError("No LLM providers configured")

        with self._lock:
            n = len(self._providers)
            for _ in range(n):
                config = self._providers[self._index % n]
                self._index = (self._index + 1) % n
                if self._is_available(config.name):
                    return self._get_or_create_client(config), config.name

            import time

            soonest = min(
                self._providers, key=lambda p: self._rate_limited.get(p.name, 0)
            )
            return self._get_or_create_client(soonest), soonest.name


# Singleton registry
_registry: Optional[LLMProviderRegistry] = None
_registry_lock = threading.Lock()


def get_registry() -> LLMProviderRegistry:
    """Get the global LLM provider registry (singleton)."""
    global _registry
    if _registry is None:
        with _registry_lock:
            if _registry is None:
                _registry = LLMProviderRegistry()
    return _registry


def reset_registry():
    """Reset the registry (for testing)."""
    global _registry
    _registry = None
