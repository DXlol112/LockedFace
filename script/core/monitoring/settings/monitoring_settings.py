"""Central settings used by face monitoring."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from math import isfinite
from typing import Any


LEFT_EYE_LANDMARKS = (386, 374)
RIGHT_EYE_LANDMARKS = (159, 145)


@dataclass(frozen=True, slots=True)
class SensitivitySettings:
    """Thresholds that control face, eye and head detection sensitivity."""

    eye_open_threshold: float = 0.015
    eye_open_with_glasses_threshold: float = 0.008
    head_position_min_ratio: float = 0.35
    head_position_max_ratio: float = 0.65
    face_detection_confidence: float = 0.5
    face_tracking_confidence: float = 0.5

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any]) -> SensitivitySettings:
        """Create validated sensitivity settings from a config section."""
        defaults = cls()

        def get_ratio(name: str, default: float) -> float:
            try:
                value = float(values.get(name, default))
            except (TypeError, ValueError):
                return default
            return value if isfinite(value) and 0.0 <= value <= 1.0 else default

        minimum = get_ratio(
            "head_position_min_ratio", defaults.head_position_min_ratio
        )
        maximum = get_ratio(
            "head_position_max_ratio", defaults.head_position_max_ratio
        )
        if minimum > maximum:
            minimum = defaults.head_position_min_ratio
            maximum = defaults.head_position_max_ratio

        return cls(
            eye_open_threshold=get_ratio(
                "eye_open_threshold", defaults.eye_open_threshold
            ),
            eye_open_with_glasses_threshold=get_ratio(
                "eye_open_with_glasses_threshold",
                defaults.eye_open_with_glasses_threshold,
            ),
            head_position_min_ratio=minimum,
            head_position_max_ratio=maximum,
            face_detection_confidence=get_ratio(
                "face_detection_confidence", defaults.face_detection_confidence
            ),
            face_tracking_confidence=get_ratio(
                "face_tracking_confidence", defaults.face_tracking_confidence
            ),
        )


DEFAULT_SENSITIVITY = SensitivitySettings()
