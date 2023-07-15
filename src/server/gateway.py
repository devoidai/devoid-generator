import logging

from typing import Dict
from fastapi import WebSocket, WebSocketDisconnect
from image_gen.avg_time import AvgTimeCalc
from image_gen import ImageGenerator, GenerationRequest
from enums import *

class WebsocketManager():    
    services: Dict[str, str]
    connections: Dict[str, WebSocket]
    generator: ImageGenerator
     
    def __init__(
            self, 
            services: Dict[str, str],
            generator: ImageGenerator
        ) -> None:
        self.services = services
        self.connections = {}
        self.generator = generator
    
    async def endpoint(self, websocket: WebSocket, service: str):
        if not self.verify_token(websocket, service):
            await websocket.close(reason="Invalid token")
            return
        
        service = Service(service)
        await self.connect(websocket, service)
        
        try:
            while True:
                message = await websocket.receive_json()
                if message["message_type"] == MessageType.REQUEST.value:
                    logging.info(f'New request from {service.name}')
                    request = GenerationRequest(service, message, self.send_message)

                    executors = AvgTimeCalc.executors.get(request.executor)
                    if executors is None or len(executors) == 0:
                        async with request.lock:
                            logging.warning(f'No executors avaible for {request.executor.name}')
                            await request.set_error('No executors avaible')
                            await request.send_to_client()
                        continue
                    
                    if request.executor == ExecutorType.AUTOMATIC1111:
                        async with self.generator.automatic1111_queue.lock:
                            self.generator.add_automatic1111_request(request)
                    elif request.executor == ExecutorType.KANDINSKY:
                        async with self.generator.kandinsky_queue.lock:
                            self.generator.add_kandinsky_request(request)

                    async with request.lock:
                        if request.executor == ExecutorType.AUTOMATIC1111:
                            await request.set_queued((self.generator.automatic1111_queue.general_size,\
                                self.generator.automatic1111_queue.premium_size))
                            await request.send_to_client()
                        elif request.executor == ExecutorType.KANDINSKY:
                            await request.set_queued((self.generator.kandinsky_queue.general_size,\
                                self.generator.kandinsky_queue.premium_size))
                            await request.send_to_client()
        except WebSocketDisconnect:
            logging.warning("Client disconnected")
        finally:
            await self.disconnect(service)
    
    def verify_token(self, websocket: WebSocket, service: str):
        token = websocket.headers.get("authorization")
        if not service in self.services.keys():
            if not self.services.get(service) == token:
                logging.error(f'Invalid token for service {service}')
                return False
        return True
    
    async def connect(self, websocket: WebSocket, service: Service):
        logging.info(f'New ws connection for service {service.name}')
        await websocket.accept()
        self.connections[service] = websocket

    async def disconnect(self, service: Service):
        if service in self.connections.keys():
            try:
                await self.connections[service].close(reason="Server forced disconnect")
                logging.info(f'Closing ws connection for service {service.name}')
                del self.connections[service]
            except Exception as e:
                logging.error(f'Error closing ws connection for service {service.name}: {e}')
    
    async def send_message(self, service: Service, json_message):
        websocket = self.connections.get(service)
        if websocket is None:
            raise Exception(f'No websocket connection for service {service.name}')
        await websocket.send_json(json_message)

    async def broadcast(self, json_message):
        '''Broadcasts message to all connected clients'''
        for websocket in self.connections.values():
            await websocket.send_json(json_message)