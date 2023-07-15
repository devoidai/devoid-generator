from enums import *
from bson.objectid import ObjectId

from typing import Union, Tuple
from collections.abc import Coroutine

from utils.database import DevoidDatabase

from .avg_time import AvgTimeCalc

from asyncio import Lock

class GenerationRequest():
    object_id: ObjectId
    service: Service
        
    message_type: MessageType
    executor: ExecutorType
    gen_type: GenType
    
    settings: dict
    service_info: dict
    payload: dict
    
    # Response fields
    gen_status: GenStatus
    result_type: Union[ContentType, None]
    result: Union[str, None]
    file_name: Union[str, None]
    
    lock: Lock
    
    def __init__(
            self, 
            service: Service, 
            message: dict,
            ws_handler: Coroutine
        ) -> None:
        self.object_id = None
        self.service = service
        self.message_type = MessageType(message.get('message_type'))
        self.executor = ExecutorType(message.get('executor'))
        self.gen_type = GenType(message.get('gen_type'))
        self.settings = message.get('settings')
        self.service_info = message.get('service_info')
        self.payload = message.get('payload')
        # Response fields
        self.gen_status = GenStatus.QUEUED
        self.result_type = None
        self.result_image = None
        self.error_message = None
        self.file_name = None
        # Websocket Message Sender
        self.avg_time = None
        self.ws_handler = ws_handler
        
        self.lock = Lock()
        
    async def save(self) -> None:
        if self.object_id is None:
            result = await DevoidDatabase.insert_request(self.as_dict())
            self.object_id = result.inserted_id
        else:
            await DevoidDatabase.update_request(self.object_id, self.as_dict())

    async def set_ok(self, result_type: ContentType, result, file_name) -> None:
        self.gen_status = GenStatus.OK
        self.result_type = result_type
        self.result = result
        self.file_name = file_name
        await self.save()
    
    async def send_to_client(self):
        if self.gen_status in [GenStatus.QUEUED, GenStatus.GENERATING]:
            await self.ws_handler(self.service, self.as_short_dict())
        else:
            await self.ws_handler(self.service, self.as_dict())
    
    async def set_queued(self, queue_size: Tuple[int, int]) -> None:
        self.gen_status = GenStatus.QUEUED

        queue_size = sum(queue_size)
        gen_count = AvgTimeCalc.executors.get(self.executor)
        if gen_count is None or len(gen_count) == 0:
            self.avg_time = None
        elif self.executor == ExecutorType.AUTOMATIC1111:
            self.avg_time = (AvgTimeCalc.auto_avg_time * queue_size) / len(gen_count)
            if self.avg_time < 4:
                self.avg_time = 4
        elif self.executor == ExecutorType.KANDINSKY:
            self.avg_time = (AvgTimeCalc.kand_avg_time * queue_size) / len(gen_count)
            if self.avg_time < 4:
                self.avg_time = 4
        
        self.avg_time = round(self.avg_time, 2)
        await self.save()
    
    async def set_generating(self) -> None:
        self.gen_status = GenStatus.GENERATING
        await self.save()
    
    async def set_error(self, message) -> None:
        self.gen_status = GenStatus.ERROR
        self.result_type = ContentType.TEXT
        self.result = message
        await self.save()
    
    def as_short_dict(self):
        return {
            'object_id': str(self.object_id),
            'service': self.service.value,
            'message_type': MessageType.RESPONSE.value,
            'executor': self.executor.value,
            'gen_type': self.gen_type.value,
            'gen_status': self.gen_status.value,
            'avg_time': self.avg_time,
            'service_info': self.service_info
        }
    
    def as_dict(self) -> dict:
        if self.gen_status == GenStatus.OK:
            result = {
                'content_type': self.result_type.value,
                'content': self.result,
                'file_name': self.file_name
            }
        elif self.gen_status == GenStatus.ERROR:
            result = {
                'content_type': self.result_type.value,
                'content': self.error_message
            }
        elif self.gen_status == GenStatus.QUEUED:
            result = None
        elif self.gen_status == GenStatus.GENERATING:
            result = None
        
        return {
            'object_id': str(self.object_id),
            'service': self.service.value,
            'message_type': MessageType.RESPONSE.value,
            'executor': self.executor.value,
            'gen_type': self.gen_type.value,
            'gen_status': self.gen_status.value,
            'result': result,
            'settings': self.settings,
            'service_info': self.service_info,
            'payload': self.payload
        }
    
    @property
    def premium(self) -> bool:
        return self.settings.get('premium')
    
    @property
    def moderate(self) -> bool:
        return self.settings.get('moderate')
    
    @property
    def sync_with_s3(self) -> bool:
        return self.settings.get('sync_with_s3')
    
    @property
    def user_id(self) -> str:
        return self.service_info.get('user_id')