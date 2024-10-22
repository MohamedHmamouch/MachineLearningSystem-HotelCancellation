import os
import sys
from hotel_cancellation.entity.config_entity import DataIngestionConfig
from hotel_cancellation.entity.artifact_entity import DataIngestionArtifact
from hotel_cancellation.exception import HotelCancellationException
from hotel_cancellation.logger import logging
from hotel_cancellation.data_access.hotel_cancellation_data import HotelCancellationData

from pandas import DataFrame
from sklearn.model_selection import train_test_split


class DataIngestion:

    def __init__(self,data_ingestion_config=DataIngestionConfig()):

        try:
            self.data_ingestion_config=data_ingestion_config

        except Exception as e:

            raise HotelCancellationException(e,sys)
        
    def export_data_into_feature_store(self)->DataFrame:



        try:

            logging.info('Exporting data from mongodb')
            hotel_cancellation_data=HotelCancellationData()

            dataframe=hotel_cancellation_data.export_collection_as_dataframe(
                collection_name=self.data_ingestion_config.collection_name
            )

            logging.info(f"data exported is {dataframe.shape}")

            feature_store_file_path=self.data_ingestion_config.feature_ingestion_file_path
            dir_path=os.path.dirname(feature_store_file_path)

            os.makedirs(dir_path,exist_ok=True)

            logging.info(f"saving exported data into feature store file paht:{feature_store_file_path}")

            dataframe.to_csv(feature_store_file_path,index=False,header=True)

            return dataframe
        
        except Exception as e:

            raise HotelCancellationException(e,sys)
        

    def split_data_train_test_split(self,dataframe:DataFrame)->None:

        try:

            train_set,test_set=train_test_split(dataframe,
                                                test_size=self.data_ingestion_config.train_test_split_ratio,shuffle=True)
            
            logging.info('Performed train test split')
            logging.info('Exited split_data_train_test')

            dir_path=os.path.dirname(self.data_ingestion_config.train_file_path)

            os.makedirs(dir_path,exist_ok=True)

            train_set.to_csv(self.data_ingestion_config.train_file_path,index=False,header=True)
            test_set.to_csv(self.data_ingestion_config.test_file_path,index=False,header=True)

            logging.info('exported train test file path')

        except Exception as e:

            raise HotelCancellationData(e,sys) from e
        

    def initiate_data_ingestion(self)->DataIngestionArtifact:


        try:
            dataframe = self.export_data_into_feature_store()

            logging.info("Got the data from mongodb")

            self.split_data_train_test_split(dataframe)

            logging.info("Performed train test split on the dataset")

            logging.info(
                "Exited initiate_data_ingestion method of Data_Ingestion class"
            )

            data_ingestion_artifact = DataIngestionArtifact(trained_file_path=self.data_ingestion_config.train_file_path,
            test_file_path=self.data_ingestion_config.test_file_path)
            
            logging.info(f"Data ingestion artifact: {data_ingestion_artifact}")
            return data_ingestion_artifact
        except Exception as e:
            raise HotelCancellationException(e, sys) from e









