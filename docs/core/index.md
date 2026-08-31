# Core-слой LockedFace

## Назначение документации

Этот раздел описывает внутреннюю логику LockedFace из `script/core`: хранение
настроек, пути приложения, локализацию, логирование, определение версии и
мониторинг пользователя по видеопотоку.

Каждому Python-модулю с собственной логикой соответствует отдельная страница.
Служебные `__init__.py` рассмотрены в разделе экспортов.

## Карта модулей

| Исходный модуль | Документация | Назначение |
| --- | --- | --- |
| `script/core/config.py` | [Конфигурация](config.md) | Чтение, сохранение и частичное обновление `config.json` |
| `script/core/i18n.py` | [Локализация](i18n.md) | Установка и смена переводов Qt |
| `script/core/logger.py` | [Логирование](logger.md) | Файловые, консольные и Qt-логи |
| `script/core/path_utils.py` | [Пути приложения](path_utils.md) | Каталоги ресурсов и пользовательских данных |
| `script/core/version.py` | [Версия и обновления](version.md) | Git-тег и последний GitHub Release |
| `script/core/monitoring/def_collection.py` | [Рабочий поток](monitoring/def_collection.md) | Камера, MediaPipe и показ предупреждающего медиа |
| `script/core/monitoring/settings/monitoring_checks.py` | [Проверки кадра](monitoring/settings/monitoring_checks.md) | Лицо, глаза и положение головы |
| `script/core/monitoring/settings/monitoring_settings.py` | [Чувствительность](monitoring/settings/monitoring_settings.md) | Landmarks и пороги распознавания |
| `script/core/monitoring/settings/monitoring_timers.py` | [Таймеры мониторинга](monitoring/settings/monitoring_timers.md) | Сессия, паузы, задержки и cooldown |

## Место core в приложении

`LockedFace.py` создаёт `QApplication`, настраивает имя приложения, включает
логирование и устанавливает сохранённый язык. UI импортирует основные функции
через пакеты `script` и `script.core`.

```text
LockedFace.py
├── path_utils        → каталог приложения и пользовательских данных
├── logger            → app.log, error.log, консоль и сообщения Qt
├── config            → config.json
├── i18n              → QTranslator
├── version           → локальный тег и GitHub Releases
└── UI
    └── VideoThread   → камера, проверки, таймеры и предупреждение
```

Core не управляет навигацией и виджетами напрямую. Исключение — `VideoThread`
наследует `QThread` и сообщает UI о кадрах и завершении через Qt-сигналы.

## Поток мониторинга

```text
MainPage
    → VideoThread(file, gaze, glasses_enabled, work_time)
    → cv2.VideoCapture(0)
    → MediaPipe FaceMesh.process(frame)
    → run_detection_checks(...)
    → DetectionStatus
    → MonitoringTimers.should_show_alert(...)
    ├── False → кадр камеры в change_pixmap_signal
    └── True  → изображение или видео в окне OpenCV
```

При завершении рабочий поток освобождает камеру и плееры, удаляет временную
копию медиа и отправляет `finished_signal`.

## Экспорты пакетов

### `script/core/__init__.py`

Публичный интерфейс верхнего уровня:

- пути: `get_application_dir`, `get_data_dir`, `get_config_path`, `get_log_dir`,
  `get_media_dir`;
- конфигурация: `load_config`, `save_config`, `update_config`;
- мониторинг: `VideoThread`;
- версия: `__version__`, `get_latest_version`, `get_lastest_verison`.

Функции локализации и логирования импортируются вызывающим кодом из своих
модулей и в `script.core.__all__` не входят.

### `script/core/monitoring/__init__.py`

Пакет экспортирует:

- рабочий поток: `VideoThread`;
- типы: `DetectionStatus`, `MonitoringTimers`, `SensitivitySettings`,
  `TimerSettings`;
- defaults и landmarks: `DEFAULT_SENSITIVITY`, `DEFAULT_TIMER_SETTINGS`,
  `LEFT_EYE_LANDMARKS`, `RIGHT_EYE_LANDMARKS`;
- проверки: `check_eyes`, `check_face`, `check_head_position`,
  `get_face_landmarks`, `is_eye_open`, `is_head_turned_away`,
  `run_detection_checks`.

### `script/core/monitoring/settings/__init__.py`

Вложенный пакет объединяет API трёх модулей настроек. Он экспортирует
`DEFAULT_SENSITIVITY`, `DEFAULT_TIMER_SETTINGS`, `LEFT_EYE_LANDMARKS`,
`RIGHT_EYE_LANDMARKS`, `DetectionStatus`, `MonitoringTimers`,
`SensitivitySettings`, `TimerSettings`, `check_eyes`, `check_face`,
`check_head_position`, `get_face_landmarks`, `is_eye_open`,
`is_head_turned_away` и `run_detection_checks`. `def_collection.py` использует
именно этот уровень импорта.

Опечатка `get_lastest_verison` сохранена как compatibility alias и является
частью текущего экспортируемого API.

## Данные и каталоги

```text
application_dir/
├── static/
├── script/style/
└── translations/

data_dir/
├── config.json
├── log/
│   ├── app.log
│   └── error.log
└── media/
```

Каталог данных выбирается через `LOCKEDFACE_DATA_DIR` или
`QStandardPaths.AppLocalDataLocation`. Ресурсы приложения находятся отдельно и
в one-folder сборке располагаются рядом с исполняемым файлом.

## Связь с UI

| Core API | Основной потребитель |
| --- | --- |
| `load_config`, `update_config` | `MainPage`, `SettingsPage`, `FilePage` |
| `get_media_dir` | `FilePage` |
| `set_application_language` | точка входа и `SettingsPage` |
| `__version__`, `get_latest_version` | `MainPage`, `SettingsPage` |
| `VideoThread` | `MainPage` |
| `change_pixmap_signal` | `MainPage.update_video_image()` |
| `finished_signal` | `MainPage.on_video_finished()` |

Подробная документация потребителей находится в [разделе UI](../ui/index.md).

## Расширение core

При добавлении нового модуля:

1. определите, является ли его API внутренним или публичным;
2. добавьте нужные переэкспорты в соответствующий `__init__.py`;
3. избегайте импорта UI из core, чтобы не создавать циклические зависимости;
4. передавайте результаты фоновой работы сигналами, если их должен получить
   главный поток Qt;
5. добавьте отдельную страницу в `docs/core` и ссылку в таблицу модулей.

## Текущие ограничения core-слоя

- Схема и типы значений `config.json` не валидируются централизованно.
- Некоторые getters создают каталоги как побочный эффект.
- Версия определяется запуском Git при импорте модуля.
- Проверка обновлений синхронная и не кешируется.
- Камера зафиксирована на индексе `0`.
- Мониторинг смешивает анализ кадров, управление ресурсами и показ окна
  предупреждения в одном методе `VideoThread.run()`.
- Часть ошибок мониторинга выводится через `print`, а не через logging.

## Связанные страницы

- [Конфигурация](config.md)
- [Пути приложения](path_utils.md)
- [Локализация](i18n.md)
- [Логирование](logger.md)
- [Версия и обновления](version.md)
- [Рабочий поток мониторинга](monitoring/def_collection.md)
- [UI-слой](../ui/index.md)
