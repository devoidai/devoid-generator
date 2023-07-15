import asyncio
import logging

from enums import *
from os import getenv

from utils.storage import Storage
from ..queue import RequestQueue
from ..request import GenerationRequest
from ..avg_time import AvgTimeCalc

class AbstractExecutor:
    name: str
    gpu: str
    timeout: float
    model: str
    exec_type: ExecutorType
    endpoint: str

    alive: bool = False

    save_images_locally = int(getenv('SAVE_IMAGES_LOCALLY'))
    images_path = getenv('IMAGES_PATH')
    image_get_url = getenv('S3_IMAGE_ENDPOINT')

    def __init__(
            self,
            name: str,
            executor_type: ExecutorType,
            gpu: str,
            timeout: float,
            model: str,
            endpoint: str
        ) -> None:
        self.name = name
        self.exec_type = executor_type
        self.gpu = gpu
        self.timeout = timeout
        self.model = model
        self.endpoint = endpoint

    async def ping(self) -> bool:
        raise NotImplementedError('Implement `ping` before using the executor')

    async def text2img(self, request: GenerationRequest):
        raise NotImplementedError('`text2img` not implemented')

    async def mix2img(self, request: GenerationRequest):
        raise NotImplementedError('`mix2img` not implemented')
    
    async def img2img(self, request: GenerationRequest):
        raise NotImplementedError('`img2img` not implemented')
    
    async def loop(self, queue: RequestQueue):
        while True:
            try:
                # Alive loop
                if not self.alive:
                    if await self.ping():
                        AvgTimeCalc.add_executor(self)                            
                        self.alive = True
                        logging.info(f'`{self.name}` is now working!')
                    else:
                        logging.debug(f'`{self.name}` is still sleeping!')
                        await asyncio.sleep(15)
                    continue

                # Waiting for request in queue
                request = await queue.get_request()
                if request is None:
                    await asyncio.sleep(0.1)
                    continue

                # Generating new request
                async with request.lock:
                    await request.set_generating()
                    await request.send_to_client()
                    logging.info(f'{self.name} processing request:{str(request.object_id)}')
                try:
                    if request.gen_type == GenType.TEXT2IMG:
                        await self.text2img(request)
                    elif request.gen_type == GenType.IMG2IMG:
                        await self.img2img(request)
                    elif request.gen_type == GenType.MIX2IMG:
                        await self.mix2img(request)
                    # logging.info(f'{self.name} processed request:{str(request.object_id)}')
                except Exception as e:
                    logging.error(f'Error while {request.gen_type.value} {str(request.object_id)}\n[{type(e)}] {e}')
                    AvgTimeCalc.remove_executor(self)
                    self.alive = False
                    logging.info(f'`{self.name}` is sleeping!')
                    async with request.lock:
                        await request.set_error(f'[{type(e)}] {e}')
                        await request.send_to_client()
            except Exception as e:
                logging.error(f'Error in executor loop `{self.name}`\n[{type(e)}] {e}')

    def save_locally(
            self,
            image_bytes,
            file_name
        ) -> None:
        with open(file_name, 'wb') as f:
            f.write(image_bytes)

    async def save_to_s3_with_event(
            self,
            request,
            images_bytes,
            file_name
        ) -> None:
        try:
            image_url = await self.save_to_s3(images_bytes, file_name, True)
            async with request.lock:
                await request.set_ok(ContentType.IMAGE_URL, image_url, file_name)
        except Exception as e:
            logging.error(f'Error while saving image {str(request.object_id)}\n[{type(e)}] {e}')
            async with request.lock:
                await request.set_error(f'[{type(e)}] {e}')
        finally:
            async with request.lock:
                await request.send_to_client()
            logging.info(f'{self.name} processed request:{str(request.object_id)}')

    async def save_to_s3(
            self, 
            image_bytes, 
            file_name, 
            sync = False
        ) -> str:
        '''returns image url'''
        if sync:
            await Storage.upload_image_bytes(image_bytes, file_name)
        else:
            loop = asyncio.get_running_loop()
            loop.create_task(Storage.upload_image_bytes(image_bytes, file_name))
        return f'{self.image_get_url}{file_name}'

    