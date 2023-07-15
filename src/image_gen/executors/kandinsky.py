import httpx
import logging
import asyncio

from os import getenv

from enums import *

from .executor import AbstractExecutor
from ..request import GenerationRequest

from ..avg_time import AvgTimeCalc

client = httpx.AsyncClient()

class KandinskyExecutor(AbstractExecutor):
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
            response = await client.get(url=self.endpoint, timeout=2, \
                headers={'authorization': getenv('KANDINSKY_API_TOKEN'), 'ngrok-skip-browser-warning': '1'})
            if response.content == b'{"RestAPI":"Kandinskiy 2.1 Model","website":"https://web.devoid.pics/"}':
                return True
            return False
        except Exception as e:
            logging.debug(e)
            return False

    @AvgTimeCalc.calc_kand_time_diff
    async def text2img(self, request: GenerationRequest):
        # Sending api request
        payload = request.payload
        response = await client.post(url=f'{self.endpoint}/text2img',\
            json=payload, timeout=self.timeout, follow_redirects=True,\
            headers={'authorization': getenv('KANDINSKY_API_TOKEN'), 'ngrok-skip-browser-warning': '1'})
        
        # Getting result
        image_bytes = response.content
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

    @AvgTimeCalc.calc_kand_time_diff
    async def img2img(self, request: GenerationRequest):
        # Sending api request
        payload = request.payload
        response = await client.post(url=f'{self.endpoint}/img2img',\
            json=payload, timeout=self.timeout, follow_redirects=True,\
            headers={'authorization': getenv('KANDINSKY_API_TOKEN'), 'ngrok-skip-browser-warning': '1'})
        
        # Getting result
        image_bytes = response.content
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

    @AvgTimeCalc.calc_kand_time_diff
    async def mix2img(self, request: GenerationRequest):
        # Sending api request
        payload = request.payload
        response = await client.post(url=f'{self.endpoint}/mix2images',\
            json=payload, timeout=self.timeout, follow_redirects=True,\
            headers={'authorization': getenv('KANDINSKY_API_TOKEN'), 'ngrok-skip-browser-warning': '1'})
        
        # Getting result
        image_bytes = response.content
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