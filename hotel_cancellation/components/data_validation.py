import json 
import sys

import pandas as pd

from evidently.model_profile  import Profile
from evidently.profile_sections import DataDriftProfileSection

from pandas import DataFrame

from hotel_cancellation.exception import HotelCancellationException
from hotel_cancellation.logger import logging
from hotel_cancellation.utils.main_utils import read_yaml_file, write_yaml_file
from hotel_cancellation.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
from hotel_cancellation.entity.config_entity import DataValidationConfig
from hotel_cancellation.constants import SCHEMA_FILE_PATH


class DataValidation:

    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,data_validation_config:DataValidationConfig):


        try:

            self.data_ingestion_artifact=data_ingestion_artifact
            self.data_validation_config=data_validation_config
            self._schema_config=read_yaml_file(file_path=SCHEMA_FILE_PATH)

        except Exception as e:

            raise HotelCancellationException(e,sys)
        

    def validate_number_of_columns(self,dataframe:DataFrame)->bool:

        try:
            status=len(dataframe.columns)==len(self._schema_config['columns'])

            logging.info(f"Is required column present: [{status}]")

            return status
        except Exception as e:

            raise HotelCancellationException(e,sys)
        
    def is_column_exist(self,df:DataFrame)->bool:


        try:
            dataframe_columns=df.columns
            missing_numerical_columns=[]
            missing_categorical_columns=[]

            for col in self._schema_config['numerical_columns']:

                if col not in dataframe_columns:

                    missing_numerical_columns.append(col)


            if len(missing_numerical_columns)>0:

                logging.info(f"missing numerical column {missing_numerical_columns}")

            
            for column in self._schema_config['categorical_columns']:

                if column not in dataframe_columns:

                    missing_categorical_columns.append(column)

            
            if len(missing_categorical_columns)>0:

                logging.info(f"Missing categorical columns {missing_categorical_columns}")


            return False if len(missing_categorical_columns)>0 or len(missing_numerical_columns)>0 else True
        
        except Exception as e:

            raise HotelCancellationException(e,sys)
        
    @staticmethod
    def read_data(file_path)->DataFrame:

        try:
            return pd.read_csv(file_path)
        
        except Exception as e:

            raise HotelCancellationException(e,sys)
        

    def detect_data_drift(self,reference_df:DataFrame,current_df:DataFrame)->bool:


        try:

            data_drift_profile=Profile(sections=[DataDriftProfileSection()])

            data_drift_profile.calculate(reference_df,current_df)

            report=data_drift_profile.json()

            json_report=json.loads(report)

            write_yaml_file(
                file_path=self.data_validation_config.drift_report_file_path,content=json_report)
            
            
            n_features=json_report['data_drift']['data']['metrics']['n_features']

            n_drifted_features=json_report['data_drift']['data']['metrics']['n_drifted_features']

            logging.info(f'{n_drifted_features}/{n_features} drift detected')

            drift_status=json_report['data_drift']['data']['metrics']['dataset_drift']

            return drift_status

        except Exception as e:

            raise HotelCancellationException(e,sys) from e


    def initiate_data_validation(self)->DataValidationArtifact:

        try:

            validation_error_msg=""

            logging.info("starting data validation")

            train_df,test_df=(
                DataValidation.read_data(file_path=self.data_ingestion_artifact.trained_file_path),
                DataValidation.read_data(file_path=self.data_ingestion_artifact.test_file_path)
            )        

            status=self.validate_number_of_columns(dataframe=train_df)

            logging.info(f'All required column are present in dataframe {status}')

            if not status:

                validation_error_msg+=f"columns are missing in training dataframe"

            status=self.validate_number_of_columns(dataframe=test_df)


            logging.info(f"all required columns present in test datframe {status}")

            if not status:
                validation_error_msg += f"Columns are missing in test dataframe."

            status = self.is_column_exist(df=train_df)

            if not status:
                validation_error_msg += f"Columns are missing in training dataframe."
            status = self.is_column_exist(df=test_df)

            if not status:
                validation_error_msg += f"columns are missing in test dataframe."

            validation_status = len(validation_error_msg) == 0

            if validation_status:
                drift_status = self.detect_data_drift(train_df, test_df)
                if drift_status:
                    logging.info(f"Drift detected.")
                    validation_error_msg = "Drift detected"
                else:
                    validation_error_msg = "Drift not detected"
            else:
                logging.info(f"Validation_error: {validation_error_msg}")
                

            data_validation_artifact = DataValidationArtifact(
                validation_status=validation_status,
                message=validation_error_msg,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )

            logging.info(f"Data validation artifact: {data_validation_artifact}")
            return data_validation_artifact
        except Exception as e:
            raise HotelCancellationException(e, sys) from e