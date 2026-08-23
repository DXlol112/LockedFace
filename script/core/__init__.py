"""Core module with video processing and utilities."""

from script.core.path_utils import (
    get_application_dir,
    get_data_dir,
    get_config_path,
    get_log_dir,
    get_media_dir,
)
from script.core.config import load_config, save_config, update_config
from script.core.version import __version__

from script.core.def_collection import VideoThread

__all__ = [
    "get_application_dir",
    "get_data_dir",
    "get_config_path",
    "get_log_dir",
    "get_media_dir",
    "load_config",
    "save_config",
    "update_config",
    "VideoThread",
    "__version__",
]
