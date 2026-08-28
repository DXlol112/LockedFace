"""Central settings used by face monitoring."""

from dataclasses import dataclass


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


DEFAULT_SENSITIVITY = SensitivitySettings()
