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
DEFAULT_LANGUAGE: Final = "RU"
SUPPORTED_LANGUAGES: Final = {"RU", "EN"}


def normalize_language(language: object) -> str:
    """Return a supported UI language code, falling back to Russian."""
    normalized = str(language).upper()
    return normalized if normalized in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def install_translation(app: QApplication, locale: str | None = None) -> QTranslator | None:
    """Install the best matching compiled ``.qm`` translation, if one exists.

    The Russian source texts remain visible when no translation is available.
    ``locale`` is used by the language selector and explicit startup choice.
    """
    locale_name = (locale or QLocale.system().name()).replace("-", "_")
    language_code = locale_name.split("_", maxsplit=1)[0].lower()
    candidates = (locale_name, language_code)
    translations_dir = get_application_dir() / TRANSLATIONS_DIR / language_code

    for candidate in dict.fromkeys(candidates):
        translator = QTranslator(app)
        if translator.load(f"{TRANSLATION_PREFIX}{candidate}", str(translations_dir)):
            app.installTranslator(translator)
            logger.info("Loaded translation for locale %s", candidate)
            return translator

    logger.debug("No translation found for locale %s", locale_name)
    return None


def set_application_language(
    app: QApplication, language: object
) -> QTranslator | None:
    """Apply RU/EN to the running application and retain its translator."""
    language_code = normalize_language(language)
    if getattr(app, "language_code", None) == language_code:
        return getattr(app, "translator", None)

    current_translator = getattr(app, "translator", None)
    if current_translator is not None:
        app.removeTranslator(current_translator)

    translator = (
        install_translation(app, language_code.lower())
        if language_code == "EN"
        else None
    )
    app.translator = translator  # type: ignore[attr-defined]
    app.language_code = language_code  # type: ignore[attr-defined]

    if language_code == "EN" and translator is None:
        logger.warning("English translation catalog could not be loaded")
    else:
        logger.info("Application language changed to %s", language_code)
    return translator
