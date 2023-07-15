import httpx
import base64
import logging
import asyncio

from enums import *

from .executor import AbstractExecutor
from ..request import GenerationRequest
from ..avg_time import AvgTimeCalc

client = httpx.AsyncClient()

class Automatic1111Executor(AbstractExecutor):
    def __init__(
            self, 
            name: str, 
            executor_type: ExecutorType,
            gpu: str, 
            timeout: float, 
            model: str, 
            endpoint: str
        ) -> None:
        super().__init__(name, executor_type, gpu, timeout, model, endpoint)

    async def ping(self):
        try: 
            response = await client.get(url=self.endpoint[:-8], timeout=5)
            if response.content == b'{"detail":"Not Found"}':
                return True
            return False
        except Exception as e:
            logging.debug(type(e))
            return False

    @AvgTimeCalc.calc_auto_time_diff
    async def text2img(self, request: GenerationRequest):
        # Sending api request
        payload = request.payload
        response = await client.post(url=f'{self.endpoint}/txt2img',\
            json=payload, timeout=self.timeout, follow_redirects=True)
        
        # Getting result
        result = response.json()
        image_bytes = base64.b64decode(result['images'][0].split(",",1)[0])
        file_name = f'{str(request.object_id)}.jpg'

        # Saving locally if needed
        if self.save_images_locally:
            self.save_locally(image_bytes, file_name)

        loop = asyncio.get_event_loop()
        loop.create_task(self.save_to_s3_with_event(request, image_bytes, file_name))

        # # Saving to S3
        # image_url = await self.save_to_s3(image_bytes, file_name, request.sync_with_s3)

        # # Mark request as done
        # async with request.lock:
        #     await request.set_ok(ContentType.IMAGE_URL, image_url, file_name)

    @AvgTimeCalc.calc_auto_time_diff
    async def img2img(self, request: GenerationRequest):
        # Sending api request
        payload = request.payload
        response = await client.post(url=f'{self.endpoint}/img2img',\
            json=payload, timeout=self.timeout, follow_redirects=True)
        
        # Getting result
        result = response.json()
        image_bytes = base64.b64decode(result['images'][0].split(",",1)[0])
        file_name = f'{str(request.object_id)}.jpg'

        # Saving locally if needed
        if self.save_images_locally:
            self.save_locally(image_bytes, file_name)

        loop = asyncio.get_event_loop()
        loop.create_task(self.save_to_s3_with_event(request, image_bytes, file_name))

        # # Saving to S3
        # image_url = await self.save_to_s3(image_bytes, file_name, request.sync_with_s3)

        # # Mark request as done
        # async with request.lock:
        #     await request.set_ok(ContentType.IMAGE_URL, image_url, file_name)