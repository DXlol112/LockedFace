# Модуль `monitoring_timers.py`

## Назначение модуля

`script/core/monitoring/settings/monitoring_timers.py` хранит длительности и
изменяемое временное состояние одной сессии: начало работы, паузы, нарушения и
cooldown после закрытия предупреждения.

## Место в архитектуре

`VideoThread.run()` создаёт один `MonitoringTimers` на запуск потока. На каждом
кадре он проверяет рабочее время и передаёт `DetectionStatus` в
`should_show_alert()`.

Модуль сам не получает системное время. Все методы принимают `current_time`,
что позволяет тестировать их детерминированно.

## Dataclass `TimerSettings`

Неизменяемая dataclass со slots:

```python
TimerSettings(
    eyes_lost_delay=1.3,
    head_turned_delay=1.0,
    alert_cooldown=3.0,
    pause_frame_delay=0.05,
)
```

| Поле | Секунды | Назначение |
| --- | ---: | --- |
| `eyes_lost_delay` | `1.3` | Сколько должно длиться отсутствие лица/глаз |
| `head_turned_delay` | `1.0` | Сколько должна длиться неправильная позиция головы |
| `alert_cooldown` | `3.0` | Пауза между закрытым и новым предупреждением |
| `pause_frame_delay` | `0.05` | Sleep между кадрами в режиме паузы |

### `from_mapping(values) -> TimerSettings`

Создаёт настройки из секции `monitoring_settings` файла `config.json`.
Нечисловые, бесконечные и отрицательные задержки заменяются defaults. Нулевые
задержки допустимы.

## `DEFAULT_TIMER_SETTINGS`

Константа содержит `TimerSettings()` со стандартными значениями. Этот
неизменяемый экземпляр безопасно используется как общий аргумент по умолчанию.

## Dataclass `MonitoringTimers`

Изменяемая dataclass со slots, представляющая одну сессию.

| Поле | Default | Назначение |
| --- | --- | --- |
| `session_started_at` | обязательное | Время запуска сессии |
| `eyes_lost_started_at` | `None` | Начало непрерывного нарушения лица/глаз |
| `head_turned_started_at` | `None` | Начало непрерывного поворота головы |
| `cooldown_until` | `0.0` | Момент окончания cooldown |
| `pause_started_at` | `None` | Начало активной паузы |
| `total_pause_duration` | `0.0` | Сумма завершённых пауз |

## Справочник методов

### `begin_pause(current_time: float) -> None`

Записывает начало паузы, только если пауза ещё не активна.

**Изменение состояния:** `pause_started_at = current_time` при прежнем `None`.

**Важные условия:** повторный вызов не сдвигает начало уже идущей паузы.

### `end_pause(current_time: float) -> None`

Завершает активную паузу.

**Изменение состояния:** добавляет
`current_time - pause_started_at` к `total_pause_duration` и сбрасывает
`pause_started_at = None`.

**Важные условия:** без активной паузы метод ничего не делает. Отрицательная
разница времени отдельно не проверяется.

### `is_work_time_finished(current_time: float, work_time: float) -> bool`

Вычисляет активное время:

```text
elapsed = current_time - session_started_at - total_pause_duration
```

Возвращает `elapsed >= work_time`.

**Побочные эффекты:** отсутствуют.

**Важные условия:** текущая незавершённая пауза ещё не входит в
`total_pause_duration`. В `VideoThread` метод во время паузы не вызывается, а
после продолжения `end_pause()` сначала обновляет сумму.

### `is_in_cooldown(current_time: float) -> bool`

Возвращает `True`, пока `current_time < cooldown_until`. Равенство означает,
что cooldown уже завершён.

### `start_cooldown(current_time: float, timer_settings: TimerSettings) -> None`

Устанавливает
`cooldown_until = current_time + timer_settings.alert_cooldown`.

**Побочные эффекты:** изменяет только состояние экземпляра. Таймеры нарушений
сбрасываются позднее в `should_show_alert()` при попадании в cooldown.

### `reset_detection_timers() -> None`

Сбрасывает `eyes_lost_started_at` и `head_turned_started_at` в `None`. Начало
сессии, паузы и cooldown не изменяет.

### `_update_violation_timer(violation_active, started_at, current_time, delay) -> tuple[float | None, bool]`

Статический helper для одного непрерывного нарушения.

**Возвращаемое значение:**

- `(None, False)`, если нарушение не активно;
- `(current_time, False)`, если оно началось только сейчас;
- `(started_at, True)`, когда длительность достигла `delay`.

**Побочные эффекты:** отсутствуют. Изменённое начало возвращается вызывающему
коду, а не записывается автоматически.

### `should_show_alert(status: DetectionStatus, current_time: float, timer_settings: TimerSettings) -> bool`

Обновляет оба таймера нарушений и сообщает, пора ли показывать предупреждение.

**Алгоритм:**

1. во время cooldown сбрасывает оба нарушения и возвращает `False`;
2. нарушение глаз активно, если лицо или глаза не обнаружены;
3. нарушение головы активно, только если лицо есть, но оно смотрит не вперёд;
4. обновляет начала через `_update_violation_timer()`;
5. возвращает `eyes_alert or head_alert`.

**Изменение состояния:** обновляет оба поля начала нарушения и может их
сбросить.

**Важные условия:** после достижения задержки метод возвращает `True` на каждом
следующем кадре, пока нарушение сохраняется. `VideoThread` предотвращает
повторное создание окна своим флагом `error_window_active`.

## Временной сценарий

```text
норма
  → нарушение глаз началось
  → 1.3 с непрерывного нарушения
  → should_show_alert == True
  → пользователь вернулся
  → предупреждение закрыто
  → cooldown 3 с, timers сброшены
  → новое нарушение начинает отсчёт заново
```

## Как добавлять таймеры

1. Добавьте задержку в `TimerSettings`.
2. Добавьте поле начала в `MonitoringTimers`.
3. Обновите `reset_detection_timers()`.
4. В `should_show_alert()` определите точное условие непрерывного нарушения.
5. Объедините результат с существующими alerts.

## Текущие ограничения

- Прямой конструктор `TimerSettings` не валидирует значения; для данных из JSON
  используется `from_mapping()`.
- Код использует передаваемые значения `time.time()`, чувствительные к
  изменению системных часов.
- Cooldown общий для всех типов нарушений.
- Причина срабатывания не возвращается, доступен только boolean.
- Класс не потокобезопасен и рассчитан на использование одним `VideoThread`.

## Связанные страницы

- [Обзор core](../../index.md)
- [Проверки кадра](monitoring_checks.md)
- [Настройки чувствительности](monitoring_settings.md)
- [Рабочий поток](../def_collection.md)
