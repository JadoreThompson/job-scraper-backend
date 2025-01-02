import os
import logging

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