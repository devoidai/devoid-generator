import asyncio
import logging

from typing import Dict
from os import getenv
from os.path import exists
from threading import Thread
from uvicorn import Config, Server
from starlette.responses import JSONResponse, FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect

from image_gen import ImageGenerator

from .schemas import *
from .gateway import WebsocketManager
from .auth_middleware import AuthMiddleware

class GeneratorRestAPI(FastAPI):
    thread: Thread
    generator: ImageGenerator
    ws_manager: WebsocketManager
    services: Dict[str, str]
    
    def __init__(
            self, 
            generator: ImageGenerator, 
            verify_tokens: bool = None
        ) -> None:
        super().__init__()
                    
        services = getenv('SERVICES').split()
        self.services = {}
        for service in services:
            values = service.split(':')
            self.services[values[0]] = values[1]
            
        self.generator = generator
        self.ws_manager = WebsocketManager(self.services, generator)
        
        self.image_get_url = getenv('API_IMAGE_GET_URL')
        self.images_path = getenv('IMAGES_PATH')
        
        # Register routes
        self.add_api_route("/", self.homepage_get, methods=["GET"])
        self.add_api_route("/img/{file_name}", self.image_get, methods=["GET"])
        self.add_api_websocket_route("/ws/{service}", self.ws_manager.endpoint)
        
        # Enable token verification
        if verify_tokens:
            auth_middleware = AuthMiddleware(self.services)
            self.add_middleware(BaseHTTPMiddleware, dispatch=auth_middleware)
        
    async def homepage_get(self):
        return JSONResponse({'RestAPI': 'Devoid Image Generator',\
            'website': 'https://web.devoid.pics/'}, status_code=200)

    async def image_get(self, file_name: str):
        '''Returns the image with the given id'''
        path = f'{self.images_path}/{file_name}'
        if not exists(path):
            return JSONResponse({"content": "Image not found"}, status_code=404)
        return FileResponse(path, media_type='image/jpg')
    
    def start(self, loop = None):
        if loop is None:
            loop = asyncio.get_running_loop()
        port = int(getenv('API_PORT'))
        server_config = Config(self, host=getenv('API_HOST'), port=port, loop=loop)
        server = Server(config=server_config)
        loop.create_task(server.serve())