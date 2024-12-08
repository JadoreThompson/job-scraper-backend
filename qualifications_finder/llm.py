import aiohttp, json

from config import HEADER, MODEL

class LLMHandler:
    prompt_template = """
    I need you to extract the requirements needed for this role in a json with 3 keys: experience which holds a list, salary which holds a float, salary type which is either\
    daily, weekly, bi-weekly, monthly or annually and location which holds a string.:
    
    Requirements: {requirements}\
    
    You must only respond with the JSON. Nothing else but  the JSON
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
    async def get_response(cls, page, payload: str) -> None:
        cls.body['messages'].append({
            'role': 'user',
            'content': cls.prompt_template.format(requirements=payload)
        })
        
        async with aiohttp.ClientSession(headers=HEADER) as session:
            async with session.post(
                url="https://api.x.ai/v1/chat/completions", 
                json=cls.body
            ) as rsp:
                if rsp.status == 200:
                    data = await rsp.json()
                    print('Data: ', json.dumps(data, indent=4))
                else:
                    print(rsp.reason)
                    