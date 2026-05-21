# Инструкция по созданию EXE файла

## Способ 1: Использование auto-py-to-exe (GUI)

1. Убедись, что виртуальное окружение активировано:
   ```
   .venv\Scripts\Activate.ps1
   ```

2. Запусти auto-py-to-exe:
   ```
   auto-py-to-exe
   ```

3. В открывшемся окне нажми на папку рядом со строкой "Script Location"

4. Выбери файл `LockedFace.py`

5. Убедись, что выставлены следующие параметры:
   - **One File**: Отключено (оставить папку/директорию)
   - **Windowed**: Включено (убрать консоль)
   - **Output directory**: `./dist`

6. В разделе **Additional files** добавь:
   - `./media` → `./media`
   - `./log` → `./log`
   - `./config.json` → `.`
   - `./script/style` → `./script/style`

7. В разделе **Hidden imports** добавь:
   ```
   PyQt6
   PyQt6.QtCore
   PyQt6.QtGui
   PyQt6.QtWidgets
   cv2
   mediapipe
   numpy
   script.core
   script.UI
   script.style
   ```

8. Нажми **Convert .py to .exe** (синяя кнопка внизу)

## Способ 2: Использование PyInstaller напрямую (командная строка)

Выполни команду:
```powershell
pyinstaller --onedir --windowed `
  --name "LockedFace" `
  --add-data "media:media" `
  --add-data "log:log" `
  --add-data "config.json:." `
  --add-data "script/style:script/style" `
  --hidden-import=PyQt6 `
  --hidden-import=PyQt6.QtCore `
  --hidden-import=PyQt6.QtGui `
  --hidden-import=PyQt6.QtWidgets `
  --hidden-import=cv2 `
  --hidden-import=mediapipe `
  --hidden-import=numpy `
  --hidden-import=script.core `
  --hidden-import=script.UI `
  --hidden-import=script.style `
  --distpath ./dist `
  LockedFace.py
```

## Результат

После выполнения в папке `./dist` появится директория `LockedFace` (не один файл!) со следующей структурой:
```
dist/
├── LockedFace/
│   ├── LockedFace.exe (основной исполняемый файл)
│   ├── media/ (скопирована папка)
│   ├── log/ (скопирована папка)
│   ├── config.json
│   ├── script/ (с папкой style внутри)
│   └── ... (другие зависимости)
```

## Запуск готового exe

Просто двойной клик на `dist/LockedFace/LockedFace.exe` или выполни в консоли:
```
./dist/LockedFace/LockedFace.exe
```

Все необходимые файлы (media, log, config.json) будут находиться в одной директории с exe файлом.
