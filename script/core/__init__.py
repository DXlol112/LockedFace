"""Core module with video processing and utilities."""

from script.core.path_utils import (
    get_base_dir,
    get_resource_path,
    get_config_path,
    get_log_dir
)

from script.core.def_collection import VideoThread

__all__ = [
    "get_base_dir",
    "get_resource_path", 
    "get_config_path",
    "get_log_dir",
    "VideoThread"
]
