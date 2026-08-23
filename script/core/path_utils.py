"""Locations used by the application at runtime.

Assets are addressed relative to the application directory. The entry point
sets that directory as the current working directory, so UI code can use plain
Qt paths such as ``static/icon/logo_icon.ico``. There is intentionally no
PyInstaller extraction-directory handling here: the project is distributed as
a one-folder application, with assets located beside the executable.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PyQt6.QtCore import QStandardPaths


PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR_ENVIRONMENT_VARIABLE = "LOCKEDFACE_DATA_DIR"


def get_application_dir() -> Path:
    """Return the directory containing the executable or the source project."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return PROJECT_DIR


def get_data_dir() -> Path:
    """Return the per-user writable data directory and create it if necessary."""
    configured_dir = os.environ.get(DATA_DIR_ENVIRONMENT_VARIABLE)
    if configured_dir:
        data_dir = Path(configured_dir)
    else:
        location = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppLocalDataLocation
        )
        data_dir = Path(location) if location else get_application_dir() / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_config_path() -> Path:
    return get_data_dir() / "config.json"


def get_log_dir() -> Path:
    log_dir = get_data_dir() / "log"
    log_dir.mkdir(exist_ok=True)
    return log_dir


def get_media_dir() -> Path:
    media_dir = get_data_dir() / "media"
    media_dir.mkdir(exist_ok=True)
    return media_dir
