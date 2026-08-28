"""Timer state and timer-related operations for face monitoring."""

from dataclasses import dataclass

from .monitoring_checks import DetectionStatus


@dataclass(frozen=True, slots=True)
class TimerSettings:
    """All monitoring delays in seconds."""

    eyes_lost_delay: float = 1.3
    head_turned_delay: float = 1.0
    alert_cooldown: float = 3.0
    pause_frame_delay: float = 0.05


DEFAULT_TIMER_SETTINGS = TimerSettings()


@dataclass(slots=True)
class MonitoringTimers:
    """Keep all session, pause, violation and cooldown timers together."""

    session_started_at: float
    eyes_lost_started_at: float | None = None
    head_turned_started_at: float | None = None
    cooldown_until: float = 0.0
    pause_started_at: float | None = None
    total_pause_duration: float = 0.0

    def begin_pause(self, current_time: float) -> None:
        if self.pause_started_at is None:
            self.pause_started_at = current_time

    def end_pause(self, current_time: float) -> None:
        if self.pause_started_at is None:
            return
        self.total_pause_duration += current_time - self.pause_started_at
        self.pause_started_at = None

    def is_work_time_finished(
        self, current_time: float, work_time: float
    ) -> bool:
        elapsed = current_time - self.session_started_at - self.total_pause_duration
        return elapsed >= work_time

    def is_in_cooldown(self, current_time: float) -> bool:
        return current_time < self.cooldown_until

    def start_cooldown(
        self, current_time: float, timer_settings: TimerSettings
    ) -> None:
        self.cooldown_until = current_time + timer_settings.alert_cooldown

    def reset_detection_timers(self) -> None:
        self.eyes_lost_started_at = None
        self.head_turned_started_at = None

    @staticmethod
    def _update_violation_timer(
        violation_active: bool,
        started_at: float | None,
        current_time: float,
        delay: float,
    ) -> tuple[float | None, bool]:
        if not violation_active:
            return None, False
        if started_at is None:
            started_at = current_time
        return started_at, current_time - started_at >= delay

    def should_show_alert(
        self,
        status: DetectionStatus,
        current_time: float,
        timer_settings: TimerSettings,
    ) -> bool:
        """Update violation timers and report whether an alert is due."""

        if self.is_in_cooldown(current_time):
            self.reset_detection_timers()
            return False

        self.eyes_lost_started_at, eyes_alert = self._update_violation_timer(
            not status.face_detected or not status.eyes_detected,
            self.eyes_lost_started_at,
            current_time,
            timer_settings.eyes_lost_delay,
        )
        self.head_turned_started_at, head_alert = self._update_violation_timer(
            status.face_detected and not status.head_looking_forward,
            self.head_turned_started_at,
            current_time,
            timer_settings.head_turned_delay,
        )
        return eyes_alert or head_alert
