"""
Unit tests for Story Mode feature.

Tests cover:
1. Story-mode prompt constants exist in all 4 locales
2. Story-mode prompt placeholders match across locales
3. Story-mode prompt formatting works
4. Project model supports mode field
5. Frontend locale files have story-mode UI strings
6. ReportAgent mode branching logic

Run with:
    cd backend && uv run pytest tests/test_story_mode.py -v
"""

import json
import os
import re
import pytest
from app.prompts import get_prompts
from app.prompts import en as en_module
from app.prompts import zh as zh_module
from app.prompts import vi as vi_module
from app.prompts import de as de_module

ALL_LOCALES = ["en", "zh", "vi", "de"]
ALL_MODULES = {"en": en_module, "zh": zh_module, "vi": vi_module, "de": de_module}

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(os.path.dirname(BACKEND_DIR), "frontend")
LOCALE_DIR = os.path.join(FRONTEND_DIR, "src", "i18n", "locales")


def _find_placeholders(text: str) -> set:
    return set(re.findall(r"(?<!\{)\{(\w+)\}(?!\})", text))


# ─────────────────────────────────────────────────────────────
# 1. Story Prompt Constants Exist
# ─────────────────────────────────────────────────────────────

STORY_CONSTANTS = [
    "STORY_PLAN_SYSTEM_PROMPT",
    "STORY_PLAN_USER_PROMPT_TEMPLATE",
    "STORY_SECTION_SYSTEM_PROMPT_TEMPLATE",
    "STORY_SECTION_USER_PROMPT_TEMPLATE",
    "SCREENPLAY_SECTION_SYSTEM_PROMPT_TEMPLATE",
    "STORY_CHAT_SYSTEM_PROMPT_TEMPLATE",
    "STORY_FALLBACK_REPORT_TITLE",
    "STORY_FALLBACK_REPORT_SUMMARY",
    "STORY_FALLBACK_SECTIONS",
]


class TestStoryPromptsExist:
    """All story-mode constants must exist in every locale."""

    @pytest.mark.parametrize("locale", ALL_LOCALES)
    @pytest.mark.parametrize("const_name", STORY_CONSTANTS)
    def test_constant_exists(self, locale, const_name):
        mod = ALL_MODULES[locale]
        assert hasattr(mod, const_name), f"{locale}.py missing constant: {const_name}"
        val = getattr(mod, const_name)
        if isinstance(val, str):
            assert len(val.strip()) > 0, f"{locale}.{const_name} is empty"


# ─────────────────────────────────────────────────────────────
# 2. Story Prompt Placeholders Match
# ─────────────────────────────────────────────────────────────

STORY_TEMPLATES = [
    "STORY_PLAN_USER_PROMPT_TEMPLATE",
    "STORY_SECTION_SYSTEM_PROMPT_TEMPLATE",
    "STORY_SECTION_USER_PROMPT_TEMPLATE",
    "SCREENPLAY_SECTION_SYSTEM_PROMPT_TEMPLATE",
    "STORY_CHAT_SYSTEM_PROMPT_TEMPLATE",
]


class TestStoryPlaceholders:
    """Story template placeholders must match across locales."""

    @pytest.mark.parametrize("name", STORY_TEMPLATES)
    @pytest.mark.parametrize("locale", ["zh", "vi", "de"])
    def test_placeholders_match_en(self, name, locale):
        en_val = getattr(en_module, name, None)
        other_val = getattr(ALL_MODULES[locale], name, None)
        if en_val is None or other_val is None:
            pytest.skip(f"{name} missing")
        en_ph = _find_placeholders(en_val)
        other_ph = _find_placeholders(other_val)
        assert en_ph == other_ph, (
            f"Placeholder mismatch {name} (en vs {locale}):\n  en={sorted(en_ph)}\n  {locale}={sorted(other_ph)}"
        )


# ─────────────────────────────────────────────────────────────
# 3. Story Prompt Formatting Works
# ─────────────────────────────────────────────────────────────

STORY_FORMAT_ARGS = {
    "STORY_PLAN_USER_PROMPT_TEMPLATE": dict(
        simulation_requirement="Harry Potter gun story",
        total_nodes=100,
        total_edges=200,
        entity_types="Person, Location",
        total_entities=50,
        related_facts_json='[{"fact":"test"}]',
    ),
    "STORY_SECTION_SYSTEM_PROMPT_TEMPLATE": dict(
        report_title="The Gun in Hogwarts",
        report_summary="A muggle boy brings a gun to a magic school",
        simulation_requirement="Harry Potter gun story",
        section_title="Chapter 1: The Arrival",
        tools_description="[tools]",
    ),
    "STORY_SECTION_USER_PROMPT_TEMPLATE": dict(
        previous_content="In the previous chapter...",
        section_title="Chapter 2: The Discovery",
    ),
    "SCREENPLAY_SECTION_SYSTEM_PROMPT_TEMPLATE": dict(
        report_title="Hogwarts",
        report_summary="A screenplay",
        simulation_requirement="HP story",
        section_title="Scene 1",
        tools_description="[tools]",
    ),
    "STORY_CHAT_SYSTEM_PROMPT_TEMPLATE": dict(
        simulation_requirement="Harry Potter story",
        report_content="The story so far...",
        tools_description="[tools]",
    ),
}


class TestStoryFormatting:
    """All story templates must format without errors."""

    @pytest.mark.parametrize("name", list(STORY_FORMAT_ARGS.keys()))
    @pytest.mark.parametrize("locale", ALL_LOCALES)
    def test_template_formats(self, name, locale):
        template = getattr(ALL_MODULES[locale], name)
        result = template.format(**STORY_FORMAT_ARGS[name])
        assert isinstance(result, str) and len(result) > 0


# ─────────────────────────────────────────────────────────────
# 4. Story Fallback Sections Structure
# ─────────────────────────────────────────────────────────────


class TestStoryFallbacks:
    """Verify story fallback sections have correct structure."""

    @pytest.mark.parametrize("locale", ALL_LOCALES)
    def test_fallback_sections_structure(self, locale):
        p = get_prompts(locale)
        sections = p.STORY_FALLBACK_SECTIONS
        assert isinstance(sections, list)
        assert len(sections) >= 2
        for s in sections:
            assert isinstance(s, dict)
            assert "title" in s
            assert "description" in s

    @pytest.mark.parametrize("locale", ALL_LOCALES)
    def test_fallback_title_not_empty(self, locale):
        p = get_prompts(locale)
        assert len(p.STORY_FALLBACK_REPORT_TITLE.strip()) > 0

    @pytest.mark.parametrize("locale", ALL_LOCALES)
    def test_fallback_summary_not_empty(self, locale):
        p = get_prompts(locale)
        assert len(p.STORY_FALLBACK_REPORT_SUMMARY.strip()) > 0


# ─────────────────────────────────────────────────────────────
# 5. Project Model Mode Field
# ─────────────────────────────────────────────────────────────


class TestProjectModel:
    """Verify Project dataclass supports mode field."""

    def test_project_has_mode_field(self):
        from app.models.project import Project
        import dataclasses

        fields = {f.name for f in dataclasses.fields(Project)}
        assert "mode" in fields
        assert "story_format" in fields

    def test_project_default_mode(self):
        from app.models.project import Project

        p = Project(
            project_id="test",
            name="test",
            status="created",
            created_at="2024-01-01",
            updated_at="2024-01-01",
            files=[],
        )
        assert p.mode == "prediction"
        assert p.story_format is None

    def test_project_story_mode(self):
        from app.models.project import Project

        p = Project(
            project_id="test",
            name="test",
            status="created",
            created_at="2024-01-01",
            updated_at="2024-01-01",
            files=[],
            mode="story",
            story_format="novel",
        )
        assert p.mode == "story"
        assert p.story_format == "novel"

    def test_project_to_dict_includes_mode(self):
        from app.models.project import Project

        p = Project(
            project_id="test",
            name="test",
            status="created",
            created_at="2024-01-01",
            updated_at="2024-01-01",
            files=[],
            mode="story",
            story_format="screenplay",
        )
        d = p.to_dict()
        assert d["mode"] == "story"
        assert d["story_format"] == "screenplay"

    def test_project_from_dict_backward_compat(self):
        from app.models.project import Project

        # Old project without mode field
        old_data = {
            "project_id": "test",
            "name": "test",
            "status": "created",
            "created_at": "2024-01-01",
            "updated_at": "2024-01-01",
            "files": [],
        }
        p = Project.from_dict(old_data)
        assert p.mode == "prediction"
        assert p.story_format is None


# ─────────────────────────────────────────────────────────────
# 6. Frontend Locale Files Have Story Keys
# ─────────────────────────────────────────────────────────────

STORY_LOCALE_KEYS = [
    "home.modePrediction",
    "home.modePredictionDesc",
    "home.modeStory",
    "home.modeStoryDesc",
    "home.formatNovel",
    "home.formatScreenplay",
    "home.console.storyPromptPlaceholder",
    "home.steps.worldBuild",
    "home.steps.characterSetup",
    "home.steps.runNarrative",
    "home.steps.storyGen",
    "home.steps.characterChat",
]


class TestStoryLocaleKeys:
    """Frontend locale files must have all story-mode UI strings."""

    def _load_and_flatten(self, locale):
        with open(os.path.join(LOCALE_DIR, f"{locale}.json"), "r") as f:
            data = json.load(f)
        return self._flatten(data)

    def _flatten(self, d, prefix=""):
        keys = {}
        for k, v in d.items():
            full = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                keys.update(self._flatten(v, full))
            else:
                keys[full] = v
        return keys

    @pytest.mark.parametrize("locale", ALL_LOCALES)
    @pytest.mark.parametrize("key", STORY_LOCALE_KEYS)
    def test_story_key_exists(self, locale, key):
        flat = self._load_and_flatten(locale)
        assert key in flat, f"Missing key '{key}' in {locale}.json"
        assert len(str(flat[key]).strip()) > 0, (
            f"Empty value for '{key}' in {locale}.json"
        )


# ─────────────────────────────────────────────────────────────
# 7. ReportAgent Mode Branching
# ─────────────────────────────────────────────────────────────


class TestReportAgentMode:
    """Verify ReportAgent accepts and stores mode."""

    def test_report_agent_accepts_mode(self):
        import inspect
        from app.services.report_agent import ReportAgent

        sig = inspect.signature(ReportAgent.__init__)
        params = list(sig.parameters.keys())
        assert "mode" in params
        assert "story_format" in params

    def test_report_agent_default_mode(self):
        from app.services.report_agent import ReportAgent

        agent = ReportAgent(
            graph_id="g1", simulation_id="s1", simulation_requirement="test"
        )
        assert agent.mode == "prediction"
        assert agent.story_format is None

    def test_report_agent_story_mode(self):
        from app.services.report_agent import ReportAgent

        agent = ReportAgent(
            graph_id="g1",
            simulation_id="s1",
            simulation_requirement="test",
            mode="story",
            story_format="novel",
        )
        assert agent.mode == "story"
        assert agent.story_format == "novel"
