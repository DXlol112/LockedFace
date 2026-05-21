"""LockedFace application package."""

from script.core import (
    get_base_dir,
    get_resource_path,
    get_config_path,
    get_log_dir,
    VideoThread
)

from script.UI import (
    StartPage,
    MainPage,
    SettingsPage,
    FilePage,
    WinDialog
)

__all__ = [
    # Core utilities
    "get_base_dir",
    "get_resource_path",
    "get_config_path",
    "get_log_dir",
    # Core processing
    "VideoThread",
    # UI pages
    "StartPage",
    "MainPage",
    "SettingsPage",
    "FilePage",
    # UI dialogs
    "WinDialog"
]
