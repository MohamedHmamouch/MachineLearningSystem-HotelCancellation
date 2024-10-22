from pandas import DataFrame
import sys

from sklearn.pipeline import Pipeline
from hotel_cancellation.exception import HotelCancellationException
from hotel_cancellation.logger import logging

class HotelCancellationModel:

    def __init__(self,preprocessing_object:Pipeline,trained_model_object:object):
        

        self.preprocessing_object=preprocessing_object
        self.trained_model_object=trained_model_object

    def predict(self,dataframe:DataFrame)->DataFrame:

        logging.info('Entered predict method')

        try:

            logging.info('Using the trained model to get prediciton')

            transformed_feature=self.preprocessing_object.transform(dataframe)

            logging.info('used the trained model to get prediction')

            return self.trained_model_object.predict(transformed_feature)
        
        except Exception as e:
            raise HotelCancellationException(e,sys) from e
        
    
    def __repr__(self):

        return f"{type(self.trained_model_object).__name__}"
    
    def __str__(self):

        return f"{type(self.trained_model_object).__name__}"
    
