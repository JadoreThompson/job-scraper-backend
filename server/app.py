from fastapi import FastAPI

# Local
from routes.stream import stream

app = FastAPI()
app.include_router(stream)