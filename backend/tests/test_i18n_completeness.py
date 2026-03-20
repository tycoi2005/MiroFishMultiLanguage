"""
Unit tests verifying all i18n work is complete.

Tests cover:
1. API messages module (bilingual error/status messages)
2. zep_tools.py to_text() bilingual output
3. Frontend locale file parity (en.json vs zh.json)
4. No remaining hardcoded Chinese in user-visible Vue templates
5. Backend service files use prompt registry (no inline Chinese prompts)

Run with:
    cd backend && uv run pytest tests/test_i18n_completeness.py -v
"""

import json
import os
import re
import pytest

# ─────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(os.path.dirname(BACKEND_DIR), "frontend")
LOCALE_DIR = os.path.join(FRONTEND_DIR, "src", "i18n", "locales")
VUE_SRC_DIR = os.path.join(FRONTEND_DIR, "src")

CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")


def _find_vue_files():
    """Find all .vue files under frontend/src/."""
    vue_files = []
    for root, dirs, files in os.walk(VUE_SRC_DIR):
        for f in files:
            if f.endswith(".vue"):
                vue_files.append(os.path.join(root, f))
    return vue_files


def _extract_template_section(filepath):
    """Extract the <template> section from a Vue SFC."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"<template>(.*?)</template>", content, re.DOTALL)
    if not match:
        return ""
    template = match.group(1)
    # Remove HTML comments
    template = re.sub(r"<!--.*?-->", "", template, flags=re.DOTALL)
    return template


def _get_service_file_content(filename):
    """Read a backend service file."""
    path = os.path.join(BACKEND_DIR, "app", "services", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _get_api_file_content(filename):
    """Read a backend API file."""
    path = os.path.join(BACKEND_DIR, "app", "api", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ─────────────────────────────────────────────────────────────
# 1. API Messages Module Tests
# ─────────────────────────────────────────────────────────────


class TestAPIMessages:
    """Test the bilingual API messages module."""

    def test_module_imports(self):
        from app.api.messages import msg, get_request_locale

        assert callable(msg)
        assert callable(get_request_locale)

    def test_msg_returns_english_by_default(self):
        from app.api.messages import msg

        result = msg("project_not_found", "en", id="test123")
        assert "test123" in result
        assert CHINESE_RE.search(result) is None

    def test_msg_returns_chinese_for_zh(self):
        from app.api.messages import msg

        result = msg("project_not_found", "zh", id="test123")
        assert "test123" in result
        assert CHINESE_RE.search(result) is not None

    def test_msg_unknown_key_returns_key(self):
        from app.api.messages import msg

        result = msg("nonexistent_key", "en")
        assert result == "nonexistent_key"

    def test_msg_with_format_kwargs(self):
        from app.api.messages import msg

        result = msg("sim_not_found", "en", id="sim_abc")
        assert "sim_abc" in result

    def test_all_messages_have_both_locales(self):
        from app.api.messages import _MESSAGES

        for key, entry in _MESSAGES.items():
            assert "en" in entry, f"Message '{key}' missing English translation"
            assert "zh" in entry, f"Message '{key}' missing Chinese translation"

    def test_all_english_messages_are_english(self):
        from app.api.messages import _MESSAGES

        for key, entry in _MESSAGES.items():
            en_text = entry["en"]
            # Allow format placeholders like {id}
            stripped = re.sub(r"\{[^}]+\}", "", en_text)
            chinese_chars = CHINESE_RE.findall(stripped)
            assert len(chinese_chars) == 0, (
                f"English message '{key}' contains Chinese: {en_text}"
            )

    def test_all_chinese_messages_contain_chinese(self):
        from app.api.messages import _MESSAGES

        for key, entry in _MESSAGES.items():
            zh_text = entry["zh"]
            if len(zh_text) > 10:  # skip very short ones
                chinese_chars = CHINESE_RE.findall(zh_text)
                assert len(chinese_chars) > 0, (
                    f"Chinese message '{key}' has no Chinese: {zh_text}"
                )


# ─────────────────────────────────────────────────────────────
# 2. zep_tools.py to_text() Bilingual Output Tests
# ─────────────────────────────────────────────────────────────


class TestZepToolsToText:
    """Test that zep_tools data classes produce bilingual to_text() output."""

    def test_search_result_to_text_en(self):
        from app.services.zep_tools import SearchResult

        sr = SearchResult(
            query="test query",
            facts=["fact1", "fact2"],
            edges=[],
            nodes=[],
            total_count=2,
        )
        text = sr.to_text(locale="en")
        assert "Search Query" in text or "search" in text.lower()
        assert "Found" in text or "2" in text
        assert CHINESE_RE.search(text) is None

    def test_search_result_to_text_zh(self):
        from app.services.zep_tools import SearchResult

        sr = SearchResult(
            query="test query", facts=["fact1"], edges=[], nodes=[], total_count=1
        )
        text = sr.to_text(locale="zh")
        assert CHINESE_RE.search(text) is not None

    def test_insight_forge_result_to_text_en(self):
        from app.services.zep_tools import InsightForgeResult

        result = InsightForgeResult(
            query="test",
            simulation_requirement="req",
            sub_queries=["q1"],
            semantic_facts=["f1"],
        )
        text = result.to_text(locale="en")
        assert CHINESE_RE.search(text) is None

    def test_insight_forge_result_to_text_zh(self):
        from app.services.zep_tools import InsightForgeResult

        result = InsightForgeResult(
            query="test",
            simulation_requirement="req",
            sub_queries=["q1"],
            semantic_facts=["f1"],
        )
        text = result.to_text(locale="zh")
        assert CHINESE_RE.search(text) is not None

    def test_panorama_result_to_text_en(self):
        from app.services.zep_tools import PanoramaResult

        result = PanoramaResult(
            query="test",
            active_facts=["af1"],
            historical_facts=["ef1"],
        )
        text = result.to_text(locale="en")
        assert CHINESE_RE.search(text) is None

    def test_panorama_result_to_text_zh(self):
        from app.services.zep_tools import PanoramaResult

        result = PanoramaResult(
            query="test",
            active_facts=["af1"],
        )
        text = result.to_text(locale="zh")
        assert CHINESE_RE.search(text) is not None

    def test_interview_result_to_text_en(self):
        from app.services.zep_tools import InterviewResult

        result = InterviewResult(
            interview_topic="test topic",
            interview_questions=["q1"],
            total_agents=5,
            interviewed_count=3,
            selection_reasoning="reason text",
            summary="summary text",
        )
        text = result.to_text(locale="en")
        assert CHINESE_RE.search(text) is None
        assert "Interview" in text or "interview" in text

    def test_interview_result_to_text_zh(self):
        from app.services.zep_tools import InterviewResult

        result = InterviewResult(
            interview_topic="test topic",
            interview_questions=["q1"],
            total_agents=5,
            interviewed_count=3,
            selection_reasoning="原因",
            summary="摘要",
        )
        text = result.to_text(locale="zh")
        assert CHINESE_RE.search(text) is not None

    def test_to_text_defaults_to_en(self):
        from app.services.zep_tools import SearchResult

        sr = SearchResult(query="test", facts=["f1"], edges=[], nodes=[], total_count=1)
        text = sr.to_text()  # no locale arg
        assert CHINESE_RE.search(text) is None


# ─────────────────────────────────────────────────────────────
# 3. Frontend Locale File Parity Tests
# ─────────────────────────────────────────────────────────────


ALL_FRONTEND_LOCALES = ["en", "zh", "vi", "de"]


class TestLocaleFiles:
    """Test that all locale JSON files have matching structures."""

    def _load_locale(self, locale):
        with open(os.path.join(LOCALE_DIR, f"{locale}.json"), "r") as f:
            return json.load(f)

    @pytest.fixture
    def en_data(self):
        return self._load_locale("en")

    @pytest.fixture
    def zh_data(self):
        return self._load_locale("zh")

    def _flatten_keys(self, d, prefix=""):
        """Flatten nested dict to dot-separated key set."""
        keys = set()
        for k, v in d.items():
            full = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                keys.update(self._flatten_keys(v, full))
            else:
                keys.add(full)
        return keys

    @pytest.mark.parametrize("locale", ALL_FRONTEND_LOCALES)
    def test_locale_json_is_valid(self, locale):
        data = self._load_locale(locale)
        assert isinstance(data, dict)
        assert len(data) > 0

    @pytest.mark.parametrize("locale", ["zh", "vi", "de"])
    def test_same_flattened_keys_as_en(self, locale):
        en_data = self._load_locale("en")
        other_data = self._load_locale(locale)
        en_keys = self._flatten_keys(en_data)
        other_keys = self._flatten_keys(other_data)
        missing = en_keys - other_keys
        extra = other_keys - en_keys
        assert not missing, f"Keys in en.json but not {locale}.json: {missing}"
        assert not extra, f"Keys in {locale}.json but not en.json: {extra}"

    def test_no_empty_values_in_en(self, en_data):
        empty = []
        for key, val in self._flatten_all(en_data):
            if isinstance(val, str) and val.strip() == "":
                empty.append(key)
        assert not empty, f"Empty values in en.json: {empty}"

    @pytest.mark.parametrize("locale", ["zh", "vi", "de"])
    def test_no_empty_values(self, locale):
        # home.descAfterSolution may be intentionally empty in some locales
        ALLOWED_EMPTY = {"home.descAfterSolution"}
        data = self._load_locale(locale)
        empty = []
        for key, val in self._flatten_all(data):
            if isinstance(val, str) and val.strip() == "" and key not in ALLOWED_EMPTY:
                empty.append(key)
        assert not empty, f"Empty values in zh.json: {empty}"

    def _flatten_all(self, d, prefix=""):
        """Yield (key, value) pairs for all leaves."""
        for k, v in d.items():
            full = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                yield from self._flatten_all(v, full)
            else:
                yield (full, v)


# ─────────────────────────────────────────────────────────────
# 4. Vue Template Chinese Text Scan
# ─────────────────────────────────────────────────────────────

# Files where Chinese in template is ACCEPTABLE (e.g. language toggle label '中文')
ALLOWED_CHINESE_IN_TEMPLATE = {
    # The language toggle displays '中文' which is correct
    "Home.vue": ["中文"],
    "MainView.vue": ["中文"],
    "SimulationView.vue": ["中文"],
    "SimulationRunView.vue": ["中文"],
    "ReportView.vue": ["中文"],
    "InteractionView.vue": ["中文"],
    "Process.vue": ["中文"],
}


class TestVueTemplates:
    """Verify no unexpected Chinese text remains in Vue templates."""

    @pytest.mark.parametrize("vue_file", _find_vue_files())
    def test_no_hardcoded_chinese_in_template(self, vue_file):
        template = _extract_template_section(vue_file)
        if not template:
            pytest.skip("No template section found")

        basename = os.path.basename(vue_file)
        allowed = ALLOWED_CHINESE_IN_TEMPLATE.get(basename, [])

        # Remove allowed Chinese strings
        cleaned = template
        for allowed_str in allowed:
            cleaned = cleaned.replace(allowed_str, "")

        chinese_matches = CHINESE_RE.findall(cleaned)
        assert len(chinese_matches) == 0, (
            f"{basename} template has {len(chinese_matches)} Chinese chars.\n"
            f"Sample: {''.join(chinese_matches[:20])}\n"
            f"Search the template for these characters to find remaining strings."
        )


# ─────────────────────────────────────────────────────────────
# 5. Backend Service Files — No Inline Chinese Prompts
# ─────────────────────────────────────────────────────────────


class TestBackendServices:
    """Verify backend service files use the prompt registry."""

    def test_report_agent_imports_get_prompts(self):
        content = _get_service_file_content("report_agent.py")
        assert (
            "from app.prompts import get_prompts" in content
            or "from ..prompts import get_prompts" in content
        )

    def test_zep_tools_imports_get_prompts(self):
        content = _get_service_file_content("zep_tools.py")
        assert (
            "from app.prompts import get_prompts" in content
            or "from ..prompts import get_prompts" in content
        )

    def test_ontology_generator_imports_get_prompts(self):
        content = _get_service_file_content("ontology_generator.py")
        assert (
            "from app.prompts import get_prompts" in content
            or "from ..prompts import get_prompts" in content
        )

    def test_simulation_config_imports_get_prompts(self):
        content = _get_service_file_content("simulation_config_generator.py")
        assert (
            "from app.prompts import get_prompts" in content
            or "from ..prompts import get_prompts" in content
        )

    def test_oasis_profile_imports_get_prompts(self):
        content = _get_service_file_content("oasis_profile_generator.py")
        assert (
            "from app.prompts import get_prompts" in content
            or "from ..prompts import get_prompts" in content
        )

    def test_report_agent_no_inline_prompt_constants(self):
        """report_agent.py should NOT define PLAN_SYSTEM_PROMPT etc inline."""
        content = _get_service_file_content("report_agent.py")
        # These constants should be in app/prompts/, not inline
        for const in [
            "PLAN_SYSTEM_PROMPT =",
            "SECTION_SYSTEM_PROMPT_TEMPLATE =",
            "CHAT_SYSTEM_PROMPT_TEMPLATE =",
            "TOOL_DESC_INSIGHT_FORGE =",
        ]:
            # Allow the comment "# Prompt moved to..."
            lines = [
                l
                for l in content.split("\n")
                if const in l and not l.strip().startswith("#")
            ]
            assert len(lines) == 0, (
                f"report_agent.py still has inline constant: {const}"
            )

    def test_api_messages_module_exists(self):
        from app.api.messages import msg, _MESSAGES

        assert len(_MESSAGES) >= 30, f"Expected 30+ messages, got {len(_MESSAGES)}"


# ─────────────────────────────────────────────────────────────
# 6. Backend API Files — No Inline Chinese in Responses
# ─────────────────────────────────────────────────────────────


class TestAPIResponses:
    """Verify API files use the messages module instead of hardcoded Chinese."""

    def _count_chinese_in_jsonify(self, content):
        """Count Chinese chars inside jsonify() calls."""
        # Find all jsonify(...) calls
        jsonify_re = re.compile(r"jsonify\(([^)]*)\)", re.DOTALL)
        chinese_count = 0
        for match in jsonify_re.finditer(content):
            inner = match.group(1)
            chinese_count += len(CHINESE_RE.findall(inner))
        return chinese_count

    def test_graph_api_no_chinese_in_jsonify(self):
        content = _get_api_file_content("graph.py")
        count = self._count_chinese_in_jsonify(content)
        assert count == 0, f"graph.py has {count} Chinese chars in jsonify() calls"

    def test_report_api_no_chinese_in_jsonify(self):
        content = _get_api_file_content("report.py")
        count = self._count_chinese_in_jsonify(content)
        assert count == 0, f"report.py has {count} Chinese chars in jsonify() calls"

    def test_simulation_api_no_chinese_in_jsonify(self):
        content = _get_api_file_content("simulation.py")
        count = self._count_chinese_in_jsonify(content)
        assert count == 0, f"simulation.py has {count} Chinese chars in jsonify() calls"

    def test_graph_api_imports_messages(self):
        content = _get_api_file_content("graph.py")
        assert (
            "from app.api.messages import" in content
            or "from .messages import" in content
        )

    def test_report_api_imports_messages(self):
        content = _get_api_file_content("report.py")
        assert (
            "from app.api.messages import" in content
            or "from .messages import" in content
        )

    def test_simulation_api_imports_messages(self):
        content = _get_api_file_content("simulation.py")
        assert (
            "from app.api.messages import" in content
            or "from .messages import" in content
        )
