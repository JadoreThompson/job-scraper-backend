import aiohttp
import asyncio
import json
import aiofiles
import logging

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
    
    def __init__(self, queue: asyncio.Queue) -> None:
        self.queue = queue
    
    async def init_handler(self) -> None:
        logger.info('Initialised LLM Handler')
        while True:
            try:
                item: any = self.queue.get_nowait()
                if isinstance(item, str):
                    await self._extract(item)
                    self.queue.task_done()
            except asyncio.queues.QueueEmpty:
                pass
            finally:
                await asyncio.sleep(0.01)
        
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
        
        await self._write_to_file(data)

    async def _write_to_file(self, data: dict) -> None:
        logger.info(f"Writing to {TRANSFORMED_FILE}")
        
        try:
            async with aiofiles.open(TRANSFORMED_FILE, 'a') as f:
                await f.write(json.dumps(data, indent=4) + '\n')
        except Exception as e:
            logger.error(f"{type(e)} {str(e)}")
            