

import os 

import sys
import numpy as np
import pandas as pd
from imblearn.combine import SMOTETomek, SMOTEENN
from sklearn.compose import make_column_transformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score,f1_score,precision_score,recall_score
from hotel_cancellation.exception import HotelCancellationException
from hotel_cancellation.logger import logging
from hotel_cancellation.utils.main_utils import load_numpy_array_data, read_yaml_file,load_object, param_dict_to_list,get_model_instance,save_object
from hotel_cancellation.entity.config_entity import ModelTrainerConfig
from hotel_cancellation.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact,ClassificationMetricArtifact
from hotel_cancellation.entity.estimator import HotelCancellationModel
from hotel_cancellation.constants import TARGET_COLUMN,SCHEMA_FILE_PATH,CURRENT_YEAR
from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

from sklearn.metrics import accuracy_score,recall_score,precision_score,f1_score





class ModelTrainer:

    def __init__(self,data_transformation_artifact:DataTransformationArtifact,
                 model_trainer_config:ModelTrainerConfig):
        

        self.data_transformation_artifact=data_transformation_artifact
        self.model_trainer_config=model_trainer_config

    def get_model_object_and_report(self,train:np.array,test:np.array):


        try:

            logging.info('start training')

            best_models={}

            model_configuration=read_yaml_file(self.model_trainer_config.model_config_file_path)

            X_train,y_train,X_test,y_test=train[:,:-1],train[:,-1],test[:,:-1],test[:,-1]

            for model_name,model_info in model_configuration['models'].items():

                model=get_model_instance(model_info['model'])

                params=model_info['params']

                params_distributions={
                    key: param_dict_to_list(value) for key,value in params.items()
                }

                logging.info(f"inititialization of {model_name} and parameters")

                random_search=RandomizedSearchCV(
                    estimator=model,
                    param_distributions=params_distributions,
                    cv=2,
                    verbose=1,
                    scoring='accuracy',
                    n_jobs=-1
                )

                random_search.fit(X_train,y_train)

                best_models[model_name]={

                    'best_estimator':random_search.best_estimator_,
                    'best_score':random_search.best_score_,
                    'best_params':random_search.best_params_
                }

                logging.info(f"end training of model {model_name}")

            

            
            for model_name, model_data in best_models.items():


                currrent_model=model_data['best_estimator']
                y_pred=currrent_model.predict(X_test)

                logging.info(f"start testing of model {model_name}")

                accuracy=accuracy_score(y_true=y_test,y_pred=y_pred)

                if accuracy>=self.model_trainer_config.accepted_accuracy:

                    best_model=currrent_model

                    break

            recall=recall_score(y_true=y_test,y_pred=y_pred)
            precision=precision_score(y_true=y_test,y_pred=y_pred)
            f_score=f1_score(y_true=y_test,y_pred=y_pred)
            accuracy=accuracy_score(y_true=y_test,y_pred=y_pred)

            metric_artifact=ClassificationMetricArtifact(

                f1_score=f_score,
                precision_score=precision,
                recall_score=recall)
                
            return best_model,metric_artifact
        
        except Exception as e:

            raise HotelCancellationException(e,sys) from e
        

    def initiate_model_trainer(self)->ModelTrainerArtifact:


        try:

            train_arr=load_numpy_array_data(
                file_path=self.data_transformation_artifact.transformed_train_file_path)

            test_arr=load_numpy_array_data(
                file_path=self.data_transformation_artifact.transformed_test_file_path
            )

            best_model,metric_artifact=self.get_model_object_and_report(
                train=train_arr,test=test_arr
            )

            processing_obj=load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)


            hotelcancellation_model=HotelCancellationModel(
                preprocessing_object=processing_obj,
                trained_model_object=best_model
            )

            logging.info('Hotel Cancellation Model with processor crreated')

            logging.info('create best model file path')

            save_object(self.model_trainer_config.trained_model_file_path,hotelcancellation_model)

            model_trainer_artifact=ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                metric_artifact=metric_artifact
            )

            logging.info(f"Model trainer artifact {model_trainer_artifact}")

            return model_trainer_artifact
        
        except Exception as e:

            raise HotelCancellationException(e,sys) from e












