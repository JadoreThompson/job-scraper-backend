import queue
import asyncio
import json
import logging
import time

from typing import List
from multiprocessing import Queue
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect as StarletteWebSocketDisconnect


logger = logging.getLogger(__name__)

class ClientManager:
    def __init__(self, server_queue: Queue) -> None:
        self.queue = server_queue
        self._connections: List[WebSocket] = []
        self._alive = False
    
    async def _loop(self) -> None:
        while True:
            try:
                data = self.queue.get_nowait()
                # asyncio.get_running_loop().create_task(self._broadcast(data))
                await self._broadcast(data)
            except queue.Empty:
                pass
            except Exception as e:
                logger.error('{} - {}'.format(type(e), str(e)))
            
            await asyncio.sleep(3)
    
    async def _broadcast(self, data: any) -> None:
        for conn in self._connections[:]:
            await asyncio.sleep(0.1)
            
            try:    
                await conn.send_text(json.dumps(data))
            except StarletteWebSocketDisconnect:
                await self.disconnect(conn)
            except Exception as e:
                logger.error('{} - {}'.format(type(e), str(e)))
    
    async def disconnect(self, websocket: WebSocket) -> None:
        try:
            await websocket.close()
            self._connections.remove(websocket)
        except Exception as e:
            logger.error('{} - {}'.format(type(e), str(e)))

    async def connect(self, websocket: WebSocket):
        if not self._alive:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:        
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            try:
                self._task = loop.create_task(self._loop())   
            except Exception as e:
                logger.error('{} - {}'.format(type(e), str(e)))
            
            self._alive = True
            
        await websocket.accept()
        self._connections.append(websocket)