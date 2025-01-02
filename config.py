import os
import logging
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

# Files
ROOT_PATH = os.path.dirname(__file__)
TRANSFORMED_FILE = ROOT_PATH + '\\jsons\\langs_only.json'
CLEANED_FILE = ROOT_PATH + '\\etl\\cleaned.csv'

# Logging
logging.basicConfig(
    filename=ROOT_PATH + '\\etl\\app.log',
    level=logging.INFO,
    format="[%(levelname)s][%(asctime)s] %(name)s - %(funcName)s - %(message)s"
)

DB_URL = f'aiosqlite://{os.getenv('DB_FILE')}'
DB_ENGINE = create_async_engine(
    DB_URL
)