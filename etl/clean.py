import aiofiles, asyncio, json
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from typing import List
from pprint import pprint

# Local
from config import TRANSFORMED_FILE, CLEANED_FILE

# Plot
def _count(language: List[str], df: pd.DataFrame) -> dict:
    count = {}
    
    for lang in language:
        count[lang] = df['experience'].apply(lambda item: lang.lower() in item.lower()).sum()
        
    return count


def _present(df: pd.DataFrame) -> None:
    len_x = 2
    len_y = 3
    fig, axs = plt.subplots(len_y, len_x, figsize=(8, 6))
    
    research_items = [
        (['python', 'java', 'c++', 'c#', 'sql', 'rust', 'javascript', 'typescript'], 'bar', 'languages'),
        (['degree', 'russel group',], 'bar', 'Education'),
        (['machine learning', 'ai', 'multithreading'], 'bar', 'Machine'),
        (['finance', 'trading'], 'bar', 'Finance'),
        (['software engineer', 'software engineering', 'software developer'], 'bar', 'Engineer Experience'),
        (['spring', 'springboot', 'flask', 'fastapi', 'django', '.net', 'rocket', 'react'], 'bar', 'Frameworks')
    ]
    
    # Plotting
    current_row = 0
    current_col = 0
    
    for idx, (titles, graph_type, title) in enumerate(research_items):
        if idx >= len_x * len_y:
            break
            
        data = _count(titles, df)
        current_axs = axs[current_row][current_col]
        
        if graph_type == 'bar':
            current_axs.bar(data.keys(), data.values(), color='skyblue')
            
        current_axs.set_title(title)
        
        if current_col == 1:
            current_col = 0
            current_row += 1
        else: 
            current_col += 1
            
    
    # Presenting
    fig.tight_layout()
    plt.show()
    

async def load_data(filepath: str) -> list:
    """
    Assumes the data isn't in a list format,
    converts to a list
    
    Args:
        filepath (str): _description_
    """    
    async with aiofiles.open(filepath, 'r') as f:
        data = await f.read()

    data = data.replace('}', '},')
    data = list(data)
    data.insert(0, '[')
    data.insert(-1, ']')
    data.pop(-1)
    data = ''.join(data)
    
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
    
    _present(df)
    

if __name__ == "__main__":
    asyncio.run(init_clean(TRANSFORMED_FILE))
