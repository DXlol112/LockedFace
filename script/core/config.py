"""Reading and writing the user configuration."""

from __future__ import annotations

import json
import logging
from typing import Any

from script.core.path_utils import get_config_path


logger = logging.getLogger(__name__)

DEFAULT_CONFIG: dict[str, Any] = {
    "selected_file": None,
    "gaze_enabled": False,
    "glasses_enabled": False,
    "work_time_seconds": 0,
}


def load_config() -> dict[str, Any]:
    """Return a complete configuration, falling back safely on malformed data."""
    config = DEFAULT_CONFIG.copy()
    config_path = get_config_path()

    if not config_path.exists():
        return config

    try:
        with config_path.open("r", encoding="utf-8") as file:
            saved_config = json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        logger.warning("Could not read configuration %s: %s", config_path, error)
        return config

    if isinstance(saved_config, dict):
        config.update(saved_config)
    else:
        logger.warning("Configuration %s does not contain a JSON object", config_path)

    return config


def save_config(config: dict[str, Any]) -> None:
    """Write a complete configuration using UTF-8."""
    with get_config_path().open("w", encoding="utf-8") as file:
        json.dump(config, file, indent=4, ensure_ascii=False)


def update_config(**values: Any) -> dict[str, Any]:
    """Merge values into the saved configuration and return the result."""
    config = load_config()
    config.update(values)
    save_config(config)
    return config
