import aiofiles, asyncio, json
import pandas as pd
from pprint import pprint

# Local
from config import SCRAPE_OUTPUT_FILE


CLEANED_FILE = 'cleaned.csv'


def count_language(language: str | list, df: pd.DataFrame) -> int:
    count = None
    
    if isinstance(language, str):
        count = df['experience'].apply(lambda item: language in item).sum()
    elif isinstance(language, list):
        for item in language:
            count[item] = df['experience'].apply(lambda item: language in item).sum()
            
    return count


def clean_data(df: pd.DataFrame):
    df = df.dropna()
    df['experience'] = df['experience'].apply(lambda item: item.strip())


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
    
    df = pd.DataFrame(data)
    df.to_csv(CLEANED_FILE, index=False)
    
    clean_data(df)

if __name__ == "__main__":
    asyncio.run(init_clean(SCRAPE_OUTPUT_FILE))
