"""LockedFace application package."""

from script.core import (
    get_application_dir,
    get_data_dir,
    get_config_path,
    get_log_dir,
    get_media_dir,
    load_config,
    save_config,
    update_config,
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
    "get_application_dir",
    "get_data_dir",
    "get_config_path",
    "get_log_dir",
    "get_media_dir",
    "load_config",
    "save_config",
    "update_config",
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
