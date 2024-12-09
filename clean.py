import aiofiles, asyncio, json
import pandas as pd

from typing import List
from pprint import pprint

# Local
from config import SCRAPE_OUTPUT_FILE


CLEANED_FILE = 'cleaned.csv'


def _count(language: List[str], df: pd.DataFrame) -> int:
    count = {}
    
    for lang in language:
        count[lang] = df['experience'].apply(lambda item: lang.lower() in item.lower()).sum()
        
    return count
    

async def load_data(filepath: str) -> list:
    """
    Assumes the data isn't in a list format,
    converts to a list
    
    Args:
        filepath (str): _description_
    """    
    async with aiofiles.open(SCRAPE_OUTPUT_FILE, 'r') as f:
        data = await f.read()

    data = data.replace('}', '},')
    data = list(data)
    data.insert(0, '[')
    data.insert(-1, ']')
    data.pop(-3)
    data = ''.join(data)
    
    async with aiofiles.open('temp.txt', 'w') as f:
        await f.write(data)
    
    return json.loads(data)


async def init_clean(json_filepath: str):
    """
    Entrypoint
    
    Args:
        filepath (str): FilePath to the JSON file
    """        
    data: list = await load_data(filepath=json_filepath)
    experience: list = []
    
    for item in data:
        if isinstance(item, dict):
            if item.get('experience', None):
                if isinstance(item['experience'], list):
                    experience.extend(item['experience'])
                elif isinstance(item['experience'], str):
                    experience.append(item['experience'])
    
    data = {'experience': experience}
    
    
    # Loading DF
    df = pd.DataFrame(data).dropna()
    df['experience'] = df['experience'].apply(lambda item: item.strip())
    
    # Insights
    print('Language: ', _count(['python', 'java', 'c++', 'c'], df))
    print('Degree: ', _count(['bachelors'], df))
    print('AI Count: ', _count(['machine learning', 'ai'], df))
    print('Finance Count: ', _count(['finance', 'trading'], df))
        

if __name__ == "__main__":
    asyncio.run(init_clean(SCRAPE_OUTPUT_FILE))
