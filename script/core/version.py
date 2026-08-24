"""Application version resolved from the latest Git tag."""

from __future__ import annotations

import subprocess
from pathlib import Path

import json
from urllib.request import Request, urlopen


LATEST_RELEASE_API_URL = (
    "https://api.github.com/repos/DXlol112/LockedFace/releases/latest"
)


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


def get_latest_version(timeout: float = 5.0) -> str:
    """Return the tag of the latest published GitHub release."""
    request = Request(
        LATEST_RELEASE_API_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "LockedFace-update-checker",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        data = json.load(response)

    tag_name = data.get("tag_name")
    if not isinstance(tag_name, str) or not tag_name.strip():
        raise ValueError("GitHub response does not contain a release tag")
    return tag_name.strip()


def get_lastest_verison(timeout: float = 5.0) -> str:
    """Compatibility alias for the old misspelled function name."""
    return get_latest_version(timeout)
