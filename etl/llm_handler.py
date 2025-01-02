import aiohttp
import asyncio
import json
import aiofiles
import logging
import multiprocessing
import queue
from uuid import uuid4

# Local
from config import TRANSFORMED_FILE

logger = logging.getLogger(__name__)


class LLMHandler:
    PROMPT_TEMPLATE = """
    I need you to extract the requirements needed for this role in a json with 3 keys: experience which holds a list, salary which holds a float, salary type which is either\
    daily, weekly, bi-weekly, monthly or annually and location which holds a string.:
    
    Requirements: {requirements}\
    
    You must only respond with the JSON. Nothing else but the JSON.\
    If there is no data to support a field and the field is a float like salary you must\
    put 0 else put None, so salary type should be None if you can't find it as well as location.\
    experience should be an empty list if you can't find it and salary should be 0 if you can't\
    find it.
    """
    
    def __init__(
        self, 
        scrape_queue, 
        server_queue=None
    ) -> None:
        self.scrape_queue = scrape_queue
        self.server_queue = server_queue
        self._count = 0
        self._data = []
    
    async def init_handler(self) -> None:
        logger.info('Initialised LLM Handler')
        
        while True:
            try:
                item: any = self.scrape_queue.get_nowait()
                if isinstance(item, str):
                    await self._extract(item)
                    if isinstance(self.scrape_queue, asyncio.Queue):
                        self.scrape_queue.task_done()
                        
            except (asyncio.queues.QueueEmpty, queue.Empty):
                pass
            except Exception as e:
                logger.error('{} - {}'.format(type(e), str(e)))
            await asyncio.sleep(0.1)
    
        
    async def _extract(self, text: str) -> None:
        langs = [
            'python', 'java', 'c++', 'c', 'kdb', 'javascript', 'typescript', 'nodejs',
            'go', 'golang', 'ruby', 'php', 'rust', 'swift', 'kotlin'
        ]
        
        data = {}
        
        data.update(
            {
                'languages': [
                    lang for lang in langs
                    if lang in text.lower()
                ]
            }
        )
        
        self._data.append(data)
        await self._route_data(data)
        
    async def _route_data(self, data: dict) -> None:
        if self.server_queue:
            self.server_queue.put_nowait(data)
        
        if self._count == 4:
            await self._write_to_file(self._data)
            self._count = 0
        else:
            self._count += 1

    async def _write_to_file(self, data: dict) -> None:
        logger.info(f"Writing to {TRANSFORMED_FILE}")
        
        try:
            async with aiofiles.open(TRANSFORMED_FILE, 'w') as f:
                await f.write(json.dumps(data, indent=4) + '\n')
        except Exception as e:
            logger.error(f"{type(e)} {str(e)}")
            