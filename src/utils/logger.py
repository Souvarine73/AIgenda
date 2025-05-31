"""
Module to configure logging using loguru.
This module sets up loguru to log messages to both the console and a file.
"""

import sys
import os
from loguru import logger


def logs_config(root_project:str, file_name:str ="app.log"):
    """
    configure loguru with the correct paths
   
    Args:
    - root_project (str): Root path of the project
    - file_name (str): Name of the lof file (default "app.log")
    """
    logger.remove()  # Remover handler por defecto
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO"
    )
    logger.add(
        os.path.join(root_project, "logs", file_name),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="DEBUG",
        rotation="1 MB"
    )