# Переводы LockedFace

Исходный язык интерфейса — русский. Все отображаемые строки помечены через
`self.tr(...)`; их подхватит `lupdate` по контексту класса.

Команды `lupdate` и `lrelease` входят в Qt 6 SDK / Qt Linguist и должны быть
доступны в `PATH` на машине, на которой готовят перевод.

Для нового языка создайте или обновите `.ts` из корня проекта:

```powershell
lupdate LockedFace.py script/UI/*.py script/UI/support_UI/*.py -ts translations/lockedface_en.ts
```

Заполните элементы `<translation>` в `translations/lockedface_en.ts` в Qt
Linguist, затем скомпилируйте каталог для `QTranslator`:

```powershell
lrelease translations/lockedface_en.ts -qm translations/lockedface_en.qm
```

Имена обязательны: `lockedface_<locale>.qm`, например
`lockedface_en.qm` или `lockedface_de_DE.qm`. При старте приложение сначала
ищет точное системное имя локали, затем только код языка. Если `.qm` не найден,
интерфейс остаётся на русском.

В `one-folder` сборке папка `translations` копируется рядом с `LockedFace.exe`.
Это позволяет добавлять и обновлять переводы без пересборки самого приложения.
