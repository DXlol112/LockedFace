import sys
from pathlib import Path

def get_base_dir():
    if hasattr(sys, "_MEIPASS"):
        # В exe от PyInstaller
        return Path(sys._MEIPASS)
    else:
        # В режиме разработки
        return Path(__file__).resolve().parent.parent.parent

def get_exe_dir():
    if hasattr(sys, "_MEIPASS"):
        return Path(sys.executable).parent
    else:
        return Path(__file__).resolve().parent.parent.parent

def get_resource_path(relative_path):
    return get_base_dir() / relative_path

def get_config_path():
    return get_base_dir() / "config.json"

def get_log_dir():
    log_dir = get_exe_dir() / "log"
    log_dir.mkdir(exist_ok=True)
    return log_dir
