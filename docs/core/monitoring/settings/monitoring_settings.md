# Модуль `monitoring_settings.py`

## Назначение модуля

`script/core/monitoring/settings/monitoring_settings.py` хранит неизменяемые
параметры чувствительности MediaPipe-проверок и индексы точек, используемых для
определения состояния глаз.

## Место в архитектуре

`VideoThread` передаёт экземпляр `SensitivitySettings` в MediaPipe FaceMesh и
`run_detection_checks()`. Функции глаз и положения головы используют тот же
объект, поэтому параметры одной сессии остаются согласованными.

## Индексы landmarks

| Константа | Значение | Назначение |
| --- | --- | --- |
| `LEFT_EYE_LANDMARKS` | `(386, 374)` | Две точки левого глаза для вертикальной дистанции |
| `RIGHT_EYE_LANDMARKS` | `(159, 145)` | Две точки правого глаза для вертикальной дистанции |

Индексы относятся к модели MediaPipe Face Mesh. Координаты landmarks
нормализованы относительно размеров кадра.

## Dataclass `SensitivitySettings`

```python
SensitivitySettings(
    eye_open_threshold=0.015,
    eye_open_with_glasses_threshold=0.008,
    head_position_min_ratio=0.35,
    head_position_max_ratio=0.65,
    face_detection_confidence=0.5,
    face_tracking_confidence=0.5,
)
```

Класс объявлен с `frozen=True` и `slots=True`: поля нельзя изменять после
создания, а произвольные новые атрибуты запрещены.

### `from_mapping(values) -> SensitivitySettings`

Создаёт настройки из секции `monitoring_settings` файла `config.json`.
Нечисловые, бесконечные и выходящие за диапазон `0.0..1.0` значения заменяются
defaults. Если нижняя граница положения головы больше верхней, обе границы
заменяются defaults.

### Поля

| Поле | Default | Где используется |
| --- | --- | --- |
| `eye_open_threshold` | `0.015` | Минимальная дистанция открытого глаза без очков |
| `eye_open_with_glasses_threshold` | `0.008` | Более низкий порог при включённой настройке очков |
| `head_position_min_ratio` | `0.35` | Нижняя граница положения носа по ширине и высоте лица |
| `head_position_max_ratio` | `0.65` | Верхняя граница положения носа |
| `face_detection_confidence` | `0.5` | `min_detection_confidence` конструктора FaceMesh |
| `face_tracking_confidence` | `0.5` | `min_tracking_confidence` конструктора FaceMesh |

### Состояние и побочные эффекты

Dataclass только хранит числа. Создание экземпляра не обращается к камере,
MediaPipe или файловой системе и не имеет побочных эффектов.

### Исключения и валидация

Прямой конструктор dataclass принимает переданные числа без проверки.
`from_mapping()` нормализует данные пользовательской конфигурации.

## `DEFAULT_SENSITIVITY`

Глобальный экземпляр `SensitivitySettings()` со всеми defaults. Он используется
как значение аргумента по умолчанию в проверках и `VideoThread`.

Экземпляр безопасно разделяется между вызовами благодаря неизменяемости
dataclass.

## Поток использования

```text
config["monitoring_settings"]
└── SensitivitySettings.from_mapping
    ├── VideoThread.__init__
    │   └── FaceMesh(confidence values)
    └── run_detection_checks
        ├── is_eye_open(eye thresholds)
        └── is_head_turned_away(head ratios)
```

## Как изменять чувствительность

### Для отдельной сессии

Создайте новый экземпляр и передайте его в `VideoThread`:

```python
sensitivity = SensitivitySettings(eye_open_threshold=0.02)
thread = VideoThread(file, gaze, glasses, work_time, sensitivity=sensitivity)
```

### Добавить новый порог

1. Добавьте поле с безопасным default в dataclass.
2. Используйте его в конкретной независимой проверке.
3. Передавайте один экземпляр по всему пути вызовов.
4. Если значение редактируется в UI, определите конфигурационный ключ,
   преобразование типа и допустимый диапазон.

### Изменить landmarks глаза

Обновите соответствующую пару индексов и проверьте их на версии Face Mesh,
используемой проектом. `is_eye_open()` ожидает минимум два допустимых индекса.

## Текущие ограничения

- Для горизонтального и вертикального положения головы используются одинаковые
  границы `min/max`.
- Алгоритм глаза использует только две точки на каждый глаз.
- Индексы привязаны к топологии MediaPipe Face Mesh.

## Связанные страницы

- [Обзор core](../../index.md)
- [Проверки кадра](monitoring_checks.md)
- [Рабочий поток](../def_collection.md)

