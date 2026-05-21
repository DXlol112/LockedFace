# Скрипт для быстрой сборки exe файла в PowerShell

Write-Host "===== Сборка LockedFace.exe =====" -ForegroundColor Cyan
Write-Host ""

# Активируем виртуальное окружение
Write-Host "Активирую виртуальное окружение..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

Write-Host "Запускаю PyInstaller..." -ForegroundColor Yellow
Write-Host ""

# Запускаем PyInstaller
pyinstaller --onedir --windowed `
  --name "LockedFace" `
  --add-data "media;media" `
  --add-data "log;log" `
  --add-data "config.json;." `
  --add-data "script/style;script/style" `
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
  --distpath dist `
  LockedFace.py

Write-Host ""
Write-Host "===== Сборка завершена! =====" -ForegroundColor Green
Write-Host ""
Write-Host "EXE файл находится в: dist\LockedFace\LockedFace.exe" -ForegroundColor Green
Write-Host ""
Write-Host "Для запуска выполни: .\dist\LockedFace\LockedFace.exe" -ForegroundColor Cyan
