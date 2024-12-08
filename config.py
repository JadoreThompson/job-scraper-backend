import os
from dotenv import load_dotenv
from asyncio.queues import Queue


load_dotenv()


QUEUE = Queue()

# Grok
HEADER = {
    "Authorization": f"Bearer {os.getenv("GROK_API_KEY")}"
}
MODEL = 'grok-beta'