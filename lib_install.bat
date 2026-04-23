@echo off
chcp 65001 >nul

set /p choice="Установить OpenCV и PyQt6? (y/n): "

if /i "%choice%"=="y" (
    echo Установка библиотек...
    pip install opencv-python pyqt6
    echo Готово!
) else (
    echo Установка отменена.
)

pause
