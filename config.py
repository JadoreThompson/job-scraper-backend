import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

# Files
ROOT_PATH = os.path.dirname(__file__)
TRANSFORMED_FILE = ROOT_PATH + '\\etl\\jsons\\langs_only.json'
CLEANED_FILE = ROOT_PATH + '\\etl\\cleaned.csv'

# Logging
logging.basicConfig(
    filename=ROOT_PATH + '\\app.log',
    level=logging.INFO,
    format="[%(levelname)s][%(asctime)s] %(name)s - %(funcName)s - %(message)s"
)

DB_URL = f'sqlite:///{os.getenv('DB_FILE')}'
DB_ENGINE = create_engine(
    DB_URL,
    future=True,
    pool_size=10,
    max_overflow=10,
    echo_pool=True
)