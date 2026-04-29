# settings_manager.py — load / save settings.json
import json
import os
import logging

logger = logging.getLogger(__name__)

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")

DEFAULTS: dict = {
    "snake_color": [50, 200, 50],   # RGB list
    "grid_overlay": False,
    "sound": True,
}


def load() -> dict:
    """Load settings from disk; fall back to defaults on any error."""
    if not os.path.exists(SETTINGS_PATH):
        save(DEFAULTS.copy())
        return DEFAULTS.copy()
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Merge with defaults so new keys are always present
        merged = DEFAULTS.copy()
        merged.update(data)
        return merged
    except Exception as exc:
        logger.warning("Could not read settings.json (%s); using defaults.", exc)
        return DEFAULTS.copy()


def save(settings: dict) -> None:
    """Persist *settings* to disk."""
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception as exc:
        logger.error("Could not write settings.json: %s", exc)