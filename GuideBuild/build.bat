@echo off
REM Скрипт для быстрой сборки exe файла

echo ===== Сборка LockedFace.exe =====
echo.

REM Активируем виртуальное окружение
call .venv\Scripts\activate.bat

echo Запускаем PyInstaller...
echo.

pyinstaller --onedir --windowed ^
  --name "LockedFace" ^
  --add-data "media;media" ^
  --add-data "log;log" ^
  --add-data "config.json;." ^
  --add-data "script/style;script/style" ^
  --hidden-import=PyQt6 ^
  --hidden-import=PyQt6.QtCore ^
  --hidden-import=PyQt6.QtGui ^
  --hidden-import=PyQt6.QtWidgets ^
  --hidden-import=cv2 ^
  --hidden-import=mediapipe ^
  --hidden-import=numpy ^
  --hidden-import=script.core ^
  --hidden-import=script.UI ^
  --hidden-import=script.style ^
  --distpath dist ^
  LockedFace.py

echo.
echo ===== Сборка завершена! =====
echo.
echo EXE файл находится в: dist\LockedFace\LockedFace.exe
echo.
pause
