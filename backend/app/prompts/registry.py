"""
Prompt registry: selects prompt set based on locale.
"""

import threading

_current_locale = threading.local()


def set_locale(locale: str):
    """Set the current thread's locale (called from API layer)."""
    _current_locale.value = locale


def get_locale() -> str:
    """Get the current thread's locale, default 'en'."""
    return getattr(_current_locale, "value", "en")


def get_prompts(locale: str = None):
    """
    Return the prompt module for the given locale.

    Usage:
        p = get_prompts("en")
        p.REPORT_PLAN_SYSTEM_PROMPT
    """
    if locale is None:
        locale = get_locale()

    if locale == "zh":
        from app.prompts import zh as prompts
    elif locale == "vi":
        from app.prompts import vi as prompts
    elif locale == "de":
        from app.prompts import de as prompts
    else:
        from app.prompts import en as prompts

    return prompts
