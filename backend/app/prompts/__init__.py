"""
Bilingual prompt system for MiroFish.

Usage:
    from app.prompts import get_prompts
    p = get_prompts("en")  # or "zh"
    system_msg = p.REPORT_PLAN_SYSTEM_PROMPT
"""

from app.prompts.registry import get_prompts, get_locale

__all__ = ["get_prompts", "get_locale"]
