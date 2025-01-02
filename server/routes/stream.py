from fastapi import APIRouter, WebSocket

stream = APIRouter(prefix='/stream', tags=['stream'])

@stream.websocket('/')
async def subscribe(websocket: WebSocket):
    pass