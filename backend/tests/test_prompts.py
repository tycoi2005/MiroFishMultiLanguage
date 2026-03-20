"""
Unit tests for the bilingual prompt system.

Run with:
    cd backend && uv run pytest tests/test_prompts.py -v
"""

import re
import pytest
from app.prompts import get_prompts, get_locale
from app.prompts.registry import set_locale
from app.prompts import en as en_module
from app.prompts import zh as zh_module


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────


def _get_all_constant_names(module):
    """Return all uppercase constant names from a prompt module."""
    return {
        name
        for name in dir(module)
        if not name.startswith("_")
        and name == name.upper()
        # allow FALLBACK_SECTIONS which is a list
        or (
            not name.startswith("_")
            and name[0].isupper()
            and name.replace("_", "").isupper()
        )
    }


def _get_public_attrs(module):
    """Return dict of all public attributes."""
    return {
        name: getattr(module, name) for name in dir(module) if not name.startswith("_")
    }


def _find_placeholders(text: str) -> set:
    """Find all {placeholder} names in a string (not escaped {{ }})."""
    return set(re.findall(r"(?<!\{)\{(\w+)\}(?!\})", text))


# ─────────────────────────────────────────────────────────────
# 1. Registry Tests
# ─────────────────────────────────────────────────────────────


class TestRegistry:
    """Test the prompt registry (locale switching, defaults)."""

    def test_get_prompts_returns_en_by_default(self):
        p = get_prompts("en")
        assert hasattr(p, "PLAN_SYSTEM_PROMPT")

    def test_get_prompts_returns_zh(self):
        p = get_prompts("zh")
        assert hasattr(p, "PLAN_SYSTEM_PROMPT")

    def test_default_locale_is_en(self):
        # get_locale() should default to "en" for a fresh thread
        locale = get_locale()
        assert locale == "en"

    def test_set_and_get_locale(self):
        set_locale("zh")
        assert get_locale() == "zh"
        set_locale("en")
        assert get_locale() == "en"

    def test_get_prompts_uses_thread_locale_when_no_arg(self):
        set_locale("zh")
        p = get_prompts()
        # Should be Chinese module
        assert "专家" in p.PLAN_SYSTEM_PROMPT or "模拟" in p.PLAN_SYSTEM_PROMPT
        set_locale("en")  # cleanup

    def test_get_prompts_explicit_locale_overrides_thread(self):
        set_locale("zh")
        p = get_prompts("en")
        # Should be English despite thread locale being zh
        assert (
            "expert" in p.PLAN_SYSTEM_PROMPT.lower()
            or "prediction" in p.PLAN_SYSTEM_PROMPT.lower()
        )
        set_locale("en")  # cleanup

    def test_unknown_locale_falls_back_to_en(self):
        p = get_prompts("fr")
        assert hasattr(p, "PLAN_SYSTEM_PROMPT")


# ─────────────────────────────────────────────────────────────
# 2. Parity Tests — en and zh must have the same constants
# ─────────────────────────────────────────────────────────────


class TestParity:
    """Ensure en.py and zh.py have matching constant names."""

    def test_all_en_constants_exist_in_zh(self):
        en_attrs = _get_public_attrs(en_module)
        zh_attrs = _get_public_attrs(zh_module)
        missing = set(en_attrs.keys()) - set(zh_attrs.keys())
        assert not missing, f"Constants in en.py but missing from zh.py: {missing}"

    def test_all_zh_constants_exist_in_en(self):
        en_attrs = _get_public_attrs(en_module)
        zh_attrs = _get_public_attrs(zh_module)
        missing = set(zh_attrs.keys()) - set(en_attrs.keys())
        assert not missing, f"Constants in zh.py but missing from en.py: {missing}"

    def test_constant_types_match(self):
        """Each constant should have the same type in both locales."""
        en_attrs = _get_public_attrs(en_module)
        zh_attrs = _get_public_attrs(zh_module)
        common = set(en_attrs.keys()) & set(zh_attrs.keys())
        mismatches = []
        for name in sorted(common):
            en_type = type(en_attrs[name]).__name__
            zh_type = type(zh_attrs[name]).__name__
            if en_type != zh_type:
                mismatches.append(f"{name}: en={en_type}, zh={zh_type}")
        assert not mismatches, f"Type mismatches:\n" + "\n".join(mismatches)


# ─────────────────────────────────────────────────────────────
# 3. Placeholder Tests — templates must have matching placeholders
# ─────────────────────────────────────────────────────────────

# Constants that are templates (contain {placeholders})
TEMPLATE_CONSTANTS = [
    "PLAN_USER_PROMPT_TEMPLATE",
    "SECTION_SYSTEM_PROMPT_TEMPLATE",
    "SECTION_USER_PROMPT_TEMPLATE",
    "CHAT_SYSTEM_PROMPT_TEMPLATE",
    "REACT_OBSERVATION_TEMPLATE",
    "REACT_INSUFFICIENT_TOOLS_MSG",
    "REACT_INSUFFICIENT_TOOLS_MSG_ALT",
    "REACT_TOOL_LIMIT_MSG",
    "REACT_UNUSED_TOOLS_HINT",
    "PROFILE_INDIVIDUAL_USER_PROMPT_TEMPLATE",
    "PROFILE_GROUP_USER_PROMPT_TEMPLATE",
    "TIME_CONFIG_USER_PROMPT_TEMPLATE",
    "EVENT_CONFIG_USER_PROMPT_TEMPLATE",
    "AGENT_CONFIG_USER_PROMPT_TEMPLATE",
    "INTERVIEW_SELECT_USER_PROMPT_TEMPLATE",
    "INTERVIEW_QUESTION_USER_PROMPT_TEMPLATE",
    "INTERVIEW_SUMMARY_USER_PROMPT_TEMPLATE",
]


class TestPlaceholders:
    """Ensure template placeholders match between en and zh."""

    @pytest.mark.parametrize("name", TEMPLATE_CONSTANTS)
    def test_template_placeholders_match(self, name):
        en_val = getattr(en_module, name, None)
        zh_val = getattr(zh_module, name, None)
        if en_val is None or zh_val is None:
            pytest.skip(f"{name} missing in one locale")
        en_ph = _find_placeholders(en_val)
        zh_ph = _find_placeholders(zh_val)
        assert en_ph == zh_ph, (
            f"Placeholder mismatch in {name}:\n"
            f"  en: {sorted(en_ph)}\n"
            f"  zh: {sorted(zh_ph)}"
        )


# ─────────────────────────────────────────────────────────────
# 4. Format Tests — all templates can be formatted without error
# ─────────────────────────────────────────────────────────────

# Map template name -> dummy values for .format()
TEMPLATE_FORMAT_ARGS = {
    "PLAN_USER_PROMPT_TEMPLATE": dict(
        simulation_requirement="test requirement",
        total_nodes=100,
        total_edges=200,
        entity_types="Person, Org",
        total_entities=50,
        related_facts_json='[{"fact":"test"}]',
    ),
    "SECTION_SYSTEM_PROMPT_TEMPLATE": dict(
        report_title="Test Report",
        report_summary="Test summary",
        simulation_requirement="test requirement",
        section_title="Section 1",
        tools_description="tool desc here",
    ),
    "SECTION_USER_PROMPT_TEMPLATE": dict(
        previous_content="Previous section content...",
        section_title="Section 2",
    ),
    "CHAT_SYSTEM_PROMPT_TEMPLATE": dict(
        simulation_requirement="test requirement",
        report_content="Report body...",
        tools_description="tool desc here",
    ),
    "REACT_OBSERVATION_TEMPLATE": dict(
        tool_name="insight_forge",
        result="some result data",
        tool_calls_count=2,
        max_tool_calls=5,
        used_tools_str="insight_forge, panorama_search",
        unused_hint="Try quick_search",
    ),
    "REACT_INSUFFICIENT_TOOLS_MSG": dict(
        tool_calls_count=1,
        min_tool_calls=3,
        unused_hint="Try insight_forge",
    ),
    "REACT_INSUFFICIENT_TOOLS_MSG_ALT": dict(
        tool_calls_count=1,
        min_tool_calls=3,
        unused_hint="Try panorama_search",
    ),
    "REACT_TOOL_LIMIT_MSG": dict(
        tool_calls_count=5,
        max_tool_calls=5,
    ),
    "REACT_UNUSED_TOOLS_HINT": dict(
        unused_list="quick_search, interview",
    ),
    "PROFILE_INDIVIDUAL_USER_PROMPT_TEMPLATE": dict(
        entity_type="Person",
        entity_name="John Doe",
        entity_summary="A test person",
        attrs_str="age: 30",
        context_str="Related context...",
    ),
    "PROFILE_GROUP_USER_PROMPT_TEMPLATE": dict(
        entity_type="Organization",
        entity_name="Test Org",
        entity_summary="A test org",
        attrs_str="size: 100",
        context_str="Related context...",
    ),
    "TIME_CONFIG_USER_PROMPT_TEMPLATE": dict(
        context_truncated="simulation context...",
        max_agents_allowed=100,
    ),
    "EVENT_CONFIG_USER_PROMPT_TEMPLATE": dict(
        simulation_requirement="test requirement",
        context_truncated="context...",
        type_info="Person: 10, Org: 5",
    ),
    "AGENT_CONFIG_USER_PROMPT_TEMPLATE": dict(
        simulation_requirement="test requirement",
        entity_list_json='[{"name":"agent1"}]',
    ),
    "INTERVIEW_SELECT_USER_PROMPT_TEMPLATE": dict(
        interview_requirement="test topic",
        simulation_requirement="test requirement",
        agent_summaries_json='[{"name":"a1"}]',
        agent_count=10,
        max_agents=5,
    ),
    "INTERVIEW_QUESTION_USER_PROMPT_TEMPLATE": dict(
        interview_requirement="test topic",
        simulation_requirement="test requirement",
        agent_roles="Student, Teacher",
    ),
    "INTERVIEW_SUMMARY_USER_PROMPT_TEMPLATE": dict(
        interview_requirement="test topic",
        interview_texts="Q: How? A: Like this.",
    ),
}


class TestFormatting:
    """Ensure all templates can be formatted without KeyError."""

    @pytest.mark.parametrize("name", list(TEMPLATE_FORMAT_ARGS.keys()))
    def test_en_template_formats(self, name):
        template = getattr(en_module, name)
        args = TEMPLATE_FORMAT_ARGS[name]
        result = template.format(**args)
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.parametrize("name", list(TEMPLATE_FORMAT_ARGS.keys()))
    def test_zh_template_formats(self, name):
        template = getattr(zh_module, name)
        args = TEMPLATE_FORMAT_ARGS[name]
        result = template.format(**args)
        assert isinstance(result, str)
        assert len(result) > 0


# ─────────────────────────────────────────────────────────────
# 5. Content Tests — basic sanity checks on prompt content
# ─────────────────────────────────────────────────────────────


class TestContent:
    """Sanity checks on prompt content."""

    def test_en_prompts_are_english(self):
        """EN prompts should not contain significant Chinese text."""
        chinese_re = re.compile(r"[\u4e00-\u9fff]")
        en_attrs = _get_public_attrs(en_module)
        problems = []
        for name, val in sorted(en_attrs.items()):
            if not isinstance(val, str):
                continue
            chinese_chars = chinese_re.findall(val)
            # Allow a few Chinese chars (e.g. in examples or quotes)
            if len(chinese_chars) > 5:
                problems.append(f"{name}: {len(chinese_chars)} Chinese chars found")
        assert not problems, f"EN prompts contain Chinese text:\n" + "\n".join(problems)

    def test_zh_prompts_are_chinese(self):
        """ZH prompts should contain substantial Chinese text."""
        chinese_re = re.compile(r"[\u4e00-\u9fff]")
        zh_attrs = _get_public_attrs(zh_module)
        problems = []
        for name, val in sorted(zh_attrs.items()):
            if not isinstance(val, str):
                continue
            if len(val) < 20:
                continue  # skip short constants like headers
            chinese_chars = chinese_re.findall(val)
            if len(chinese_chars) == 0:
                problems.append(f"{name}: no Chinese chars found")
        assert not problems, f"ZH prompts missing Chinese text:\n" + "\n".join(problems)

    def test_en_plan_prompt_mentions_prediction(self):
        assert (
            "prediction" in en_module.PLAN_SYSTEM_PROMPT.lower()
            or "forecast" in en_module.PLAN_SYSTEM_PROMPT.lower()
            or "future" in en_module.PLAN_SYSTEM_PROMPT.lower()
        )

    def test_zh_plan_prompt_mentions_prediction(self):
        assert (
            "预测" in zh_module.PLAN_SYSTEM_PROMPT
            or "未来" in zh_module.PLAN_SYSTEM_PROMPT
        )

    def test_tool_descriptions_not_empty(self):
        for locale in ["en", "zh"]:
            p = get_prompts(locale)
            for tool in [
                "TOOL_DESC_INSIGHT_FORGE",
                "TOOL_DESC_PANORAMA_SEARCH",
                "TOOL_DESC_QUICK_SEARCH",
                "TOOL_DESC_INTERVIEW_AGENTS",
            ]:
                val = getattr(p, tool)
                assert isinstance(val, str) and len(val) > 50, (
                    f"{locale}.{tool} is too short or not a string"
                )

    def test_fallback_sections_is_list(self):
        for locale in ["en", "zh"]:
            p = get_prompts(locale)
            assert isinstance(p.FALLBACK_SECTIONS, list)
            assert len(p.FALLBACK_SECTIONS) >= 2
            for section in p.FALLBACK_SECTIONS:
                assert "title" in section
                assert "description" in section

    def test_fallback_question_templates_are_lists(self):
        for locale in ["en", "zh"]:
            p = get_prompts(locale)
            assert isinstance(p.SUB_QUESTION_FALLBACK_TEMPLATES, list)
            assert len(p.SUB_QUESTION_FALLBACK_TEMPLATES) >= 2
            assert isinstance(p.INTERVIEW_QUESTION_FALLBACK_TEMPLATES, list)
            assert len(p.INTERVIEW_QUESTION_FALLBACK_TEMPLATES) >= 2


# ─────────────────────────────────────────────────────────────
# 6. Non-empty Tests — every constant must be non-empty
# ─────────────────────────────────────────────────────────────


class TestNonEmpty:
    """Every prompt constant must be non-empty."""

    def test_en_constants_non_empty(self):
        en_attrs = _get_public_attrs(en_module)
        empty = [
            name
            for name, val in en_attrs.items()
            if isinstance(val, str) and len(val.strip()) == 0
        ]
        assert not empty, f"Empty EN constants: {empty}"

    def test_zh_constants_non_empty(self):
        zh_attrs = _get_public_attrs(zh_module)
        empty = [
            name
            for name, val in zh_attrs.items()
            if isinstance(val, str) and len(val.strip()) == 0
        ]
        assert not empty, f"Empty ZH constants: {empty}"
