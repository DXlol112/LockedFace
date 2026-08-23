# Переводы LockedFace

Исходный язык интерфейса — русский. Все переводимые строки помечены через
`self.tr(...)`, а переводы каждого языка хранятся в своей подпапке:

```text
translations/
└── en/
    ├── lockedface_en.ts  # редактируемый каталог
    └── lockedface_en.qm  # файл, загружаемый QTranslator
```

При запуске приложение автоматически определяет язык системы. Например, для
`en_US` оно ищет сначала `translations/en/lockedface_en_US.qm`, затем
`translations/en/lockedface_en.qm`. Если подходящего файла нет, интерфейс
остаётся на русском языке.

## Обновление английского перевода

Команды `pylupdate6` и `lrelease` должны быть доступны в `PATH`. Из корня
проекта выполните:

```powershell
$sources = @("LockedFace.py") + @(Get-ChildItem script/UI -Recurse -Filter *.py |
    ForEach-Object { Resolve-Path -Relative $_.FullName })
pylupdate6 $sources --ts translations/en/lockedface_en.ts
lrelease translations/en/lockedface_en.ts -qm translations/en/lockedface_en.qm
```

После `pylupdate6` заполните новые элементы `<translation>` в Qt Linguist и
повторно запустите `lrelease`. В one-folder сборке вся папка `translations`
копируется рядом с `LockedFace.exe`, поэтому языковые подпапки сохраняются.
