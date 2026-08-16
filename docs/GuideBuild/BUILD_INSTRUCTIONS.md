# Сборка one-folder версии

Проект собирается только в режим **one-folder**: распространяйте целиком
папку из `dist`, а не один `LockedFace.exe`. В ней ресурсы лежат в известных
местах рядом с исполняемым файлом, поэтому приложению не нужна отдельная
логика поиска временных каталогов упаковщика.

## Подготовка

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pyinstaller auto-py-to-exe
```

Если добавлялись переводы, сначала скомпилируйте нужные `.ts` в `.qm` по
[инструкции для переводов](../../translations/README.md).

## Через auto-py-to-exe

1. Запустите `auto-py-to-exe` из корня репозитория.
2. Нажмите **Load config** и выберите
   `docs\GuideBuild\bulid_config.json`.
3. Нажмите **Convert .py to .exe**.

Конфигурация включает `--contents-directory .`: PyInstaller кладёт данные и
зависимости в папку рядом с `LockedFace.exe`, а не в `_internal`. Она также
упаковывает `static`, `script/style`, `translations` и весь пакет `mediapipe`.

## Результат

После сборки передавайте пользователю папку `output\LockedFace` (или папку
`dist\LockedFace`, если собираете через командный PyInstaller) целиком. Её
важные части выглядят так:

```text
LockedFace/
├── LockedFace.exe
├── static/             # иконки
├── script/style/       # QSS
├── translations/
│   └── en/             # lockedface_en.ts и lockedface_en.qm
└── ...                 # библиотеки PyInstaller
```

Настройки, логи и выбранные пользователем медиа не попадают в каталог
установки. Windows хранит их в `QStandardPaths.AppLocalDataLocation` (обычно
в `%LOCALAPPDATA%\LockedFace\LockedFace`). Для портативного запуска или
тестов можно задать переменную окружения `LOCKEDFACE_DATA_DIR`.
