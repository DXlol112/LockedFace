"""UI module with all application pages and dialogs."""

from script.UI.start_page import StartPage
from script.UI.main_page import MainPage
from script.UI.settings_page import SettingsPage
from script.UI.file_page import FilePage
from script.UI.support_UI import WinDialog

__all__ = [
    "StartPage",
    "MainPage",
    "SettingsPage",
    "FilePage",
    "WinDialog"
]
