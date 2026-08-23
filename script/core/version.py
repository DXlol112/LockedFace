"""Application version resolved from the latest Git tag."""

from __future__ import annotations

import subprocess
from pathlib import Path


def get_version() -> str:
    """Return the latest Git tag, or a safe value outside a Git checkout."""
    repository_root = Path(__file__).resolve().parents[2]

    try:
        version = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=repository_root,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError, OSError):
        return "unknown"

    return version or "unknown"


__version__ = get_version()
