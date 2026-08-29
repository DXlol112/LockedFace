"""Independent face, eye and head-position checks."""

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

from .monitoring_settings import (
    DEFAULT_SENSITIVITY,
    LEFT_EYE_LANDMARKS,
    RIGHT_EYE_LANDMARKS,
    SensitivitySettings,
)


@dataclass(frozen=True, slots=True)
class DetectionStatus:
    """Result of all checks for one camera frame."""

    face_detected: bool
    eyes_detected: bool
    head_looking_forward: bool


def get_face_landmarks(results: Any) -> Sequence[Any] | None:
    """Return landmarks of the first detected face, if one exists."""

    faces = getattr(results, "multi_face_landmarks", None)
    if not faces:
        return None
    return faces[0].landmark


def check_face(landmarks: Sequence[Any] | None) -> bool:
    """Check whether a face was detected."""

    return landmarks is not None


def is_eye_open(
    landmarks: Sequence[Any],
    eye_indices: Sequence[int],
    glasses_enabled: bool,
    sensitivity: SensitivitySettings = DEFAULT_SENSITIVITY,
) -> bool:
    """Check one eye using the configured landmark-distance threshold."""

    first_point = landmarks[eye_indices[0]]
    second_point = landmarks[eye_indices[1]]
    distance = np.sqrt(
        (first_point.x - second_point.x) ** 2
        + (first_point.y - second_point.y) ** 2
    )
    threshold = (
        sensitivity.eye_open_with_glasses_threshold
        if glasses_enabled
        else sensitivity.eye_open_threshold
    )
    return bool(distance > threshold)


def check_eyes(
    landmarks: Sequence[Any],
    gaze_enabled: bool,
    glasses_enabled: bool,
    sensitivity: SensitivitySettings = DEFAULT_SENSITIVITY,
) -> bool:
    """Check whether at least one eye is open when gaze tracking is enabled."""

    if not gaze_enabled:
        return True

    left_eye_open = is_eye_open(
        landmarks, LEFT_EYE_LANDMARKS, glasses_enabled, sensitivity
    )
    right_eye_open = is_eye_open(
        landmarks, RIGHT_EYE_LANDMARKS, glasses_enabled, sensitivity
    )
    return left_eye_open or right_eye_open


def is_head_turned_away(
    landmarks: Sequence[Any],
    sensitivity: SensitivitySettings = DEFAULT_SENSITIVITY,
) -> bool:
    """Check whether the nose has moved too far from the face centre."""

    nose = landmarks[4]
    left_side = landmarks[234]
    right_side = landmarks[454]
    top = landmarks[10]
    bottom = landmarks[152]

    width = abs(right_side.x - left_side.x)
    if width == 0:
        return True
    horizontal_ratio = abs(nose.x - left_side.x) / width

    height = abs(bottom.y - top.y)
    if height == 0:
        return True
    vertical_ratio = abs(nose.y - top.y) / height

    minimum = sensitivity.head_position_min_ratio
    maximum = sensitivity.head_position_max_ratio
    return not (
        minimum <= horizontal_ratio <= maximum
        and minimum <= vertical_ratio <= maximum
    )


def check_head_position(
    landmarks: Sequence[Any],
    sensitivity: SensitivitySettings = DEFAULT_SENSITIVITY,
) -> bool:
    """Check whether the head is looking forward."""

    return not is_head_turned_away(landmarks, sensitivity)


def run_detection_checks(
    results: Any,
    gaze_enabled: bool,
    glasses_enabled: bool,
    sensitivity: SensitivitySettings = DEFAULT_SENSITIVITY,
) -> tuple[DetectionStatus, Sequence[Any] | None]:
    """Run every frame check and return both status and face landmarks."""

    landmarks = get_face_landmarks(results)
    face_detected = check_face(landmarks)
    if not face_detected:
        return DetectionStatus(False, False, True), None

    return (
        DetectionStatus(
            face_detected=True,
            eyes_detected=check_eyes(
                landmarks, gaze_enabled, glasses_enabled, sensitivity
            ),
            head_looking_forward=check_head_position(landmarks, sensitivity),
        ),
        landmarks,
    )
