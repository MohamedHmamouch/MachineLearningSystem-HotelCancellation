import os 

import sys
import numpy as np
import pandas as pd
from imblearn.combine import SMOTETomek, SMOTEENN
from sklearn.compose import make_column_transformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer


from hotel_cancellation.constants import TARGET_COLUMN,SCHEMA_FILE_PATH,CURRENT_YEAR
from hotel_cancellation.entity.config_entity import DataTransformationConfig
from hotel_cancellation.entity.artifact_entity import DataIngestionArtifact,DataTransformationArtifact,DataValidationArtifact
from hotel_cancellation.exception import HotelCancellationException
from hotel_cancellation.logger import logging
from hotel_cancellation.utils.main_utils import save_object,save_numpy_array_data,read_yaml_file,drop_columns

class DataTransformation:

    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,
                 data_transformation_config:DataTransformationConfig,
                 data_validation_artifact:DataValidationArtifact
                 ):
        
        try:

            self.data_ingestion_artifact=data_ingestion_artifact
            self.data_transformation_config=data_transformation_config
            self.data_validation_artifact=data_validation_artifact
            self._schema_config=read_yaml_file(file_path=SCHEMA_FILE_PATH)

        except Exception as e:

            raise HotelCancellationException(e,sys)
        

    @staticmethod
    def read_data(file_path)->pd.DataFrame:

        try:

            return pd.read_csv(file_path)
        
        except Exception as e:

            raise HotelCancellationException(e,sys)
        
    def get_transformer_object(self)->Pipeline:

        try:


            oh_transformer = OneHotEncoder(dtype=np.float64, sparse_output=False, handle_unknown='infrequent_if_exist')
            ordinal_transformer = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)

            oh_columns=self._schema_config['oh_columns']
            or_columns=self._schema_config['or_columns']

            num_columns=self._schema_config['numerical_columns']

            preprocessor=make_column_transformer(
            (Pipeline([
                ('imputer',SimpleImputer(strategy='median'))
            ]),num_columns
            ),

            (Pipeline([
                ('imputer',SimpleImputer(strategy='most_frequent')),
                ('OneHotEncoder',oh_transformer)
            ]), oh_columns),

            (Pipeline([
                ('imputer',SimpleImputer(strategy='most_frequent')),
                ('OrdinalEncoder',ordinal_transformer)
            ]),or_columns))
        
            logging.info("Created preprocessor object from ColumnTransformer")

            logging.info(
                    "Exited get_data_transformer_object method of DataTransformation class"
                )
            return preprocessor
        except Exception as e:
            raise HotelCancellationException(e,sys) from e
        
    def initiate_data_transformation(self,)->DataTransformationArtifact:

        try:

            if self.data_validation_artifact.validation_status:

                logging.info("starting data transformation")

                preprocessor=self.get_transformer_object()
                logging.info('got the preprocessor object')

                train_df=DataTransformation.read_data(file_path=self.data_ingestion_artifact.trained_file_path)
                test_df=DataTransformation.read_data(file_path=self.data_ingestion_artifact.test_file_path)

                input_feature_train_df=train_df.drop(columns=[TARGET_COLUMN],axis=1)
                target_feature_df=train_df[TARGET_COLUMN]

                logging.info('got train features and test features of training set')

                drop_cols=self._schema_config['drop_columns']

                logging.info('drop columns in drop_cols of training set')

                input_feature_train_df=drop_columns(df=input_feature_train_df,cols=drop_cols)

                input_feature_test_df=test_df.drop(columns=[TARGET_COLUMN],axis=1)
                target_feature_test_df=test_df[TARGET_COLUMN]

                logging.info('got train features and test features of testing dataset')

                logging.info('applying preprocessign object on training dataframe and testing dataframe')

                input_feature_train_arr=preprocessor.fit_transform(input_feature_train_df)

                input_feature_test_arr=preprocessor.transform(input_feature_test_df)

                smt=SMOTEENN(sampling_strategy='minority')

                input_feature_train_final,target_feature_train_final=smt.fit_resample(input_feature_train_arr,target_feature_df)

                input_feature_test_final,target_feature_test_final=smt.fit_resample(
                    input_feature_test_arr,target_feature_test_df
                )

                train_arr = np.c_[
                    input_feature_train_final, np.array(target_feature_train_final)
                ]

                test_arr = np.c_[
                    input_feature_test_final, np.array(target_feature_test_final)
                ]

                save_object(self.data_transformation_config.transformed_object_file_path, preprocessor)
                save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array=train_arr)
                save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array=test_arr)

                logging.info("Saved the preprocessor object")

                logging.info(
                    "Exited initiate_data_transformation method of Data_Transformation class"
                )

                data_transformation_artifact = DataTransformationArtifact(
                    transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                    transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                    transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
                )
                return data_transformation_artifact
            
            else:
                raise Exception(self.data_validation_artifact.message)
            
        except Exception as e:
            raise HotelCancellationException(e, sys) from e




            




        
