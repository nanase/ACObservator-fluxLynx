import logging
import logging.config

import uvicorn.logging


def create_uvicorn_logger(logger_name: str) -> logging.Logger:
    """
    Uvicorn のロガーをベースにして新しいロガーを生成します。

    :param logger_name: ロガー名を表す文字列。
    :type logger_name: str
    :return: 新たに生成されたロガー。
    :rtype: logging.Logger
    """
    logger = logging.getLogger(f"uvicorn.{logger_name}")
    logger.propagate = False
    console_handler = logging.StreamHandler()
    formatter_custom = uvicorn.logging.DefaultFormatter(
        f"%(levelprefix)s [\u001b[36m{logger_name}\u001b[0m] %(message)s"
    )

    console_handler.setFormatter(formatter_custom)
    logger.addHandler(console_handler)

    return logger
