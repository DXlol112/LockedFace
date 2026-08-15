"""QTranslator bootstrap for optional application translations."""

from __future__ import annotations

import logging
from typing import Final

from PyQt6.QtCore import QLocale, QTranslator
from PyQt6.QtWidgets import QApplication

from script.core.path_utils import get_application_dir


logger = logging.getLogger(__name__)
TRANSLATIONS_DIR: Final = "translations"
TRANSLATION_PREFIX: Final = "lockedface_"


def install_translation(app: QApplication, locale: str | None = None) -> QTranslator | None:
    """Install the best matching compiled ``.qm`` translation, if one exists.

    The Russian source texts remain visible when no translation is available.
    ``locale`` is primarily useful for tests and a future language selector.
    """
    locale_name = locale or QLocale.system().name()
    candidates = (locale_name, locale_name.split("_", maxsplit=1)[0])
    translations_dir = get_application_dir() / TRANSLATIONS_DIR

    for candidate in dict.fromkeys(candidates):
        translator = QTranslator(app)
        if translator.load(f"{TRANSLATION_PREFIX}{candidate}", str(translations_dir)):
            app.installTranslator(translator)
            logger.info("Loaded translation for locale %s", candidate)
            return translator

    logger.debug("No translation found for locale %s", locale_name)
    return None
