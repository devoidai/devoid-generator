import os
import json
import logger
import asyncio

from dotenv import load_dotenv
load_dotenv()

from server.fastapi_server import GeneratorRestAPI
from utils.database import DevoidDatabase
from utils.storage import Storage

from enums import ExecutorType
from image_gen import ImageGenerator
from image_gen.avg_time import AvgTimeCalc

async def main():
    logger.setup()
        
    AvgTimeCalc.update_ratio()
    
    loop = asyncio.get_running_loop()

    # S3 Storage
    api_host = os.getenv('S3_ENDPOINT')
    access_key = os.getenv('S3_ACCESS_KEY')
    secret_key = os.getenv('S3_SECRET_KEY')
    bucket_name = os.getenv('S3_BUCKET_NAME')
    await Storage.init(api_host, access_key, secret_key, bucket_name)

    # Image generator
    a, b = map(int, os.getenv('GENERAL_PREMIUM_RATIO').split())
    generator = ImageGenerator((a, b))
        
    # Database
    db = DevoidDatabase()
    db.connect(mongo_url=os.getenv('MONGODB_URI'), loop=loop)
    
    # Rest API
    api = GeneratorRestAPI(generator, verify_tokens=True)

    # Loading executors
    with open('data/executors.json', 'r') as file:
        executors = json.load(file)
    for executor in executors:
        name = executor.get('name')
        endpoint = executor.get('endpoint')
        gpu = executor.get('gpu')
        timeout = float(executor.get('timeout'))
        model = executor.get('model')
        exec_type = ExecutorType(executor.get('exec_type'))
        generator.add_executor(exec_type, name, endpoint, gpu, timeout, model)

    # Starting
    db.connect(os.getenv('MONGODB_URI'), loop)
    api.start(loop)
    generator.start(loop)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.create_task(main())
    loop.run_forever()