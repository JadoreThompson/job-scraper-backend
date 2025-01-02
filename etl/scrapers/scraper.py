import asyncio
import logging
from ..llm_handler import LLMHandler

logger = logging.getLogger(__name__)

class Scraper:
    _is_alive = True
    
    def __init__(self, queue: asyncio.Queue) -> None:
        self.queue = queue
        
    async def init_scraper(self) -> None: ...
    
    async def _llm_handler(self) -> None:
        while self._is_alive:
            try:
                data: any = self.queue.get_nowait()
                if data:
                    result: bool = await LLMHandler.get_response(payload=data)
                    if not result:
                        self._is_alive = False
                        
                    self.queue.task_done()
            except asyncio.queues.QueueEmpty:
                pass
            except Exception as e:
                logger.error(f"{type(e)} {str(e)}")
            
            await asyncio.sleep(0.5)