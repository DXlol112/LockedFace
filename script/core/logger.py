import logging
import sys

from logging.handlers import RotatingFileHandler

from PyQt6.QtCore import (
    qInstallMessageHandler,
    QtMsgType,
)

from script.core.path_utils import get_log_dir

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)s | "
    "%(filename)s:%(lineno)d | "
    "%(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def qt_message_handler(mode, context, message) -> None:
    """
    Перенаправляет сообщения Qt
    в стандартную систему logging.
    """

    logger = logging.getLogger("Qt")

    if mode == QtMsgType.QtDebugMsg:
        logger.debug(message)

    elif mode == QtMsgType.QtInfoMsg:
        logger.info(message)

    elif mode == QtMsgType.QtWarningMsg:
        logger.warning(message)

    elif mode == QtMsgType.QtCriticalMsg:
        logger.error(message)

    elif mode == QtMsgType.QtFatalMsg:
        logger.critical(message)

def setup_logging() -> None:
    """
    Настройка системы логирования приложения.
    """

    log_dir = get_log_dir()
    log_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    app_log = log_dir / "app.log"
    error_log = log_dir / "error.log"

    formatter = logging.Formatter(
        LOG_FORMAT,
        datefmt=DATE_FORMAT
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()

    # ----------------------------------
    # Общий лог
    # ----------------------------------

    file_handler = RotatingFileHandler(
        app_log,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )

    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)

    # ----------------------------------
    # Только ошибки
    # ----------------------------------

    error_handler = RotatingFileHandler(
        error_log,
        maxBytes=2 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )

    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    root_logger.addHandler(error_handler)

    # ----------------------------------
    # Консоль
    # ----------------------------------

    if sys.stdout is not None:
        console_handler = logging.StreamHandler(
            sys.stdout
        )

        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        root_logger.addHandler(console_handler)

    # ----------------------------------
    # Сторонние библиотеки
    # ----------------------------------

    logging.captureWarnings(True)

    logging.getLogger(
        "py.warnings"
    ).setLevel(logging.ERROR)

    logging.getLogger(
        "google"
    ).setLevel(logging.ERROR)

    logging.getLogger(
        "mediapipe"
    ).setLevel(logging.ERROR)

    # ----------------------------------
    # Qt
    # ----------------------------------

    qInstallMessageHandler(
        qt_message_handler
    )

    logger = logging.getLogger(__name__)

    logger.info(
        "Система логирования инициализирована"
    )

    logger.debug(
        "Каталог логов: %s",
        log_dir
    )
