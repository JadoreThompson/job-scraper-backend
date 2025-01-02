import asyncio
import logging
import queue
from ..llm_handler import LLMHandler

logger = logging.getLogger(__name__)

class Scraper:
    _is_alive = True
    
    def __init__(self, queue: asyncio.Queue) -> None:
        self.queue = queue
        
    async def init_scraper(self) -> None: ...
            