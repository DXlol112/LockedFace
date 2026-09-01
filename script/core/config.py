"""Reading and writing the user configuration."""

from __future__ import annotations

import json
import logging
from copy import deepcopy
from typing import Any

from script.core.path_utils import get_config_path


logger = logging.getLogger(__name__)

DEFAULT_CONFIG: dict[str, Any] = {
    "user_settings": {
        "selected_file": None,
        "work_time_seconds": 0,
        "translations_select": "RU",
    },
    "monitoring_settings": {
        "gaze_enabled": False,
        "glasses_enabled": False,
        "eyes_lost_delay": 1.3,
        "head_turned_delay": 1.0,
        "alert_cooldown": 3.0,
        "pause_frame_delay": 0.05,
        "eye_open_threshold": 0.015,
        "eye_open_with_glasses_threshold": 0.008,
        "head_position_min_ratio": 0.35,
        "head_position_max_ratio": 0.65,
        "face_detection_confidence": 0.5,
        "face_tracking_confidence": 0.5,
    },
}

def return_default_config() -> None:
    """Reset only the monitoring settings to their default values."""
    config = load_config()
    config["monitoring_settings"] = deepcopy(DEFAULT_CONFIG["monitoring_settings"])
    save_config(config)

def load_config() -> dict[str, Any]:
    """Return a complete configuration, falling back safely on malformed data."""
    config = deepcopy(DEFAULT_CONFIG)
    config_path = get_config_path()

    if not config_path.exists():
        return config

    try:
        with config_path.open("r", encoding="utf-8") as file:
            saved_config = json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        logger.warning("Could not read configuration %s: %s", config_path, error)
        return config

    if not isinstance(saved_config, dict):
        logger.warning("Configuration %s does not contain a JSON object", config_path)
        return config

    for section, values in saved_config.items():
        if section in DEFAULT_CONFIG:
            if isinstance(values, dict):
                config[section].update(values)
            else:
                logger.warning(
                    "Configuration section %s in %s is not a JSON object",
                    section,
                    config_path,
                )
        else:
            config[section] = values

    return config


def save_config(config: dict[str, Any]) -> None:
    """Write a complete configuration using UTF-8."""
    with get_config_path().open("w", encoding="utf-8") as file:
        json.dump(config, file, indent=4, ensure_ascii=False)


def update_config(section: str, **values: Any) -> dict[str, Any]:
    """Merge values into one configuration section and return the result."""
    config = load_config()
    section_config = config.get(section)
    if not isinstance(section_config, dict):
        section_config = {}
        config[section] = section_config
    section_config.update(values)
    save_config(config)
    return config
