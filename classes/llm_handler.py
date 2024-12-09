import aiohttp, asyncio, json, traceback, aiofiles

# Local
from config import HEADER, MODEL, SCRAPE_OUTPUT_FILE
from logger import CustomLogger


logger = CustomLogger(module=__name__).logger


class LLMHandler:
    prompt_template = """
    I need you to extract the requirements needed for this role in a json with 3 keys: experience which holds a list, salary which holds a float, salary type which is either\
    daily, weekly, bi-weekly, monthly or annually and location which holds a string.:
    
    Requirements: {requirements}\
    
    You must only respond with the JSON. Nothing else but the JSON.\
    If there is no data to support a field and the field is a float like salary you must\
    put 0 else put None, so salary type should be None if you can't find it as well as location.\
    experience should be an empty list if you can't find it and salary should be 0 if you can't\
    find it.
    """
    body = {
        'messages': [
            {
                'role': 'system', 
                'content': "You're an expert html parse and json formatter"
            }
        ],
        'model': MODEL
    }
    
    @classmethod
    async def get_response(cls, payload: str) -> None:
        """
        Fetches response from GROK. Injecting the requirements 
        into the prompt template
        
        Args:
            payload (str): HTML snippet of job description
        """        
        cls.body['messages'].append({
            'role': 'user',
            'content': cls.prompt_template.format(requirements=payload)
        })
        
        logger.info("Fetching response...")
        
        async with aiohttp.ClientSession(headers=HEADER) as session:
            async with session.post(
                url="https://api.x.ai/v1/chat/completions", 
                json=cls.body
            ) as rsp:
                try:
                    if rsp.status == 200:
                        data = await rsp.json()
                        data = data['choices'][0]['message']['content']
                        data = data.replace('```', '').replace('json', '')
                        data = json.loads(data)
                        
                        for k, v in data.items():
                            if v == 'None':
                                data[k] = None
                                
                        cls.body['messages'].pop(-1)
                        await cls._write_to_file(data)
                        await asyncio.sleep(1)
                    else:
                        logger.debug(f"Error fetching response: {rsp.status} - {rsp.reason}")
                    
                    logger.info("Finshed getting response")
                except (json.decoder.JSONDecodeError, Exception) as e:
                    logger.error(f"{type(e)} {str(e)}")
                    
    @classmethod
    async def _write_to_file(cls, data: dict) -> None:
        logger.info(f"Writing to {SCRAPE_OUTPUT_FILE}")
        
        try:
            async with aiofiles.open(SCRAPE_OUTPUT_FILE, 'a') as f:
                await f.write(json.dumps(data, indent=4) + '\n')
        except Exception as e:
            logger.error(f"{type(e)} {str(e)}")
            