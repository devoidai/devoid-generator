import asyncio
import logging

from os import getenv
from bson.objectid import ObjectId

import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient

from asyncio import AbstractEventLoop

class DevoidDatabase():
    '''Singleton class for database connection'''
    
    __instance = None
    '''Singleton instance'''
    __mongo_url: str
    '''MongoDB URL'''
    __database: AsyncIOMotorDatabase
    '''Database instance'''
    __client: AsyncIOMotorClient
    '''Client instance'''    
    
    def __new__(cls):
        '''Singleton constructor'''
        if cls.__instance is None:
            cls.__instance = super(DevoidDatabase, cls).__new__(cls)
        return cls.__instance
    
    @classmethod
    def connect(cls, mongo_url: str = None, loop: AbstractEventLoop = None):
        '''Connects to MongoDB by URL'''
        logging.info('Connecting to MongoDB')
        cls.__mongo_url = mongo_url
        cls.__client = motor.motor_asyncio.AsyncIOMotorClient(cls.__mongo_url, io_loop=loop)
        cls.__database = cls.__client.aibot
        cls.__database = cls.__client.get_database(getenv('MONGODB_DB'))
        logging.info('Connected to MongoDB')
    
    @classmethod
    async def insert_request(cls, request: dict) -> ObjectId:
        '''Inserts request into database'''
        return await cls.__database.requests.insert_one(request)

    @classmethod
    async def update_request(cls, id: ObjectId, request: dict) -> None:
        '''Updates request in database'''
        try:
            return await cls.__database.requests.update_one({'_id': id}, {'$set': request})
        except Exception as e:
            logging.error(e)
    
    @classmethod
    def get_loop(cls) -> AbstractEventLoop:
        '''Returns running event loop'''
        return cls.__client.get_io_loop()
    
    @classmethod
    def get_requests_table(cls) -> AsyncIOMotorDatabase:
        '''Returns requests table'''
        return cls.__database.requests
