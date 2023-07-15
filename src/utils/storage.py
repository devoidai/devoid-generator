import os
import logging 
import aioboto3 

from .compress import compress_image

class Storage():
    connected: bool
    resource = None
    s3_session: aioboto3.Session
    
    @classmethod
    async def init(
            cls,
            endpoint,
            access_key, 
            secret_key, 
            bucket_name
        ) -> None:
        cls.endpoint = endpoint
        cls.access_key = access_key
        cls.bucket_name = bucket_name
        cls.secret_key = secret_key
        cls.s3_session = aioboto3.Session()
        logging.info('S3 loaded')

    @classmethod
    async def upload_image_file(
            cls,
            image_path: str,
            file_name: str
        )-> bool:
        try:
            # Upload image to S3 storage
            resource = cls.s3_session.resource('s3', endpoint_url=cls.endpoint,\
                    aws_access_key_id=cls.access_key, aws_secret_access_key=cls.secret_key)
            async with resource as s3:
                bucket = await s3.Bucket(cls.bucket_name)
                await bucket.upload_file(image_path, file_name, ExtraArgs={'ContentType': 'image/jpeg'})
            logging.info(f'Image {file_name} successfully saved to S3 storage')
        except Exception as e:
            logging.error(f'Cannot save image to S3 storage: {e}')
        return False
    
    @classmethod
    async def upload_image_bytes(
            cls,
            image_bytes: bytes,
            file_name: str
        )-> bool:
        try:
            # Compressing image
            image_bytes = compress_image(image_bytes)
            # Upload image to S3 storage
            resource = cls.s3_session.resource('s3', endpoint_url=cls.endpoint,\
                    aws_access_key_id=cls.access_key, aws_secret_access_key=cls.secret_key)
            async with resource as s3:
                bucket = await s3.Bucket(cls.bucket_name)
                await bucket.put_object(Body=image_bytes, Key=file_name, ContentType='image/jpeg')
            logging.info(f'Image {file_name} successfully saved to S3 storage')
        except Exception as e:
            logging.error(f'Cannot save image to S3 storage: {e}')
        return False



