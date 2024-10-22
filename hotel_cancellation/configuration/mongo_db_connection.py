import os
import pymongo
import sys
from hotel_cancellation.constants import *
from hotel_cancellation.exception import HotelCancellationException
from hotel_cancellation.logger import logging
# from pymongo.errors import ConnectionFailure, AutoReconnect,BulkWriteError


class MongoDBClient:


    client=None

    def __init__(self,database_name=DATABASE_NAME)->None:

        try:

            if MongoDBClient.client is None:
                mongo_db_url=MONGODB_URL_KEY

                if mongo_db_url is None:

                    raise Exception(f"Environnement key {MONGODB_URL_KEY} is not set")
                
                MongoDBClient.client=pymongo.MongoClient(mongo_db_url,serverSelectionTimeoutMS=5000)

            self.client=MongoDBClient.client
            self.database=self.client[database_name]
            self.database_name=database_name
            logging.info('MongoDB connection is successful')
        except Exception as e:

            raise HotelCancellationException(e,sys)