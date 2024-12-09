import logging
from logging import Logger


logging.basicConfig(
    filename='app.log', 
    level=logging.INFO,
    format='%(asctime)s = %(levelname)s - %(funcName)s - %(message)s',
)


class CustomLogger:
    def __init__(self, module: str) -> None:
        self.logger: Logger = logging.getLogger(module)
