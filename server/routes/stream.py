import logging
import asyncio

from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect as StarletteWebSocketDisconnect

# Local
from ..manager import ClientManager

stream = APIRouter(prefix='/stream', tags=['stream'])
manager: ClientManager = None
logger = logging.getLogger(__name__)

@stream.websocket('/')
async def subscribe(websocket: WebSocket):
    try:
        await manager.connect(websocket)
        
        while True:
            await asyncio.sleep(1)
    except StarletteWebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error('{} - {}'.format(type(e), str(e)))
    