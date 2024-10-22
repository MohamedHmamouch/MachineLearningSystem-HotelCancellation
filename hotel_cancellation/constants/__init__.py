
import os
from datetime import date

DATABASE_NAME='hotel_cancellation'
COLLECTION_NAME="hotel_cancellation"
MONGODB_URL_KEY="mongodb+srv://mohamedhma99:321Soufinane_@cluster0.zbjqo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
PIPELINE_NAME:str='HotelConcellationPipeline'
ARTIFACT_DIR:str="artifact"
MODEL_FILE_NAME='model.pkl'
FILE_NAME: str = "Hotel_Cancellation.csv"



# constant for data ingestion

DATA_INGESTION_COLLECTION_NAME:str='hotel_cancellation'
DATA_INGESTION_DIR_NAME:str='data_ingestion'
DATA_INGESTION_FEATURE_STORE_DIR:str='feature_store'
DATA_INGESTION_INGESTED_DIR:str='ingested'
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO:float=0.2
TRAIN_FILE_NAME: str = "train.csv"
TEST_FILE_NAME: str = "test.csv"

TARGET_COLUMN="is_canceled"
CURRENT_YEAR=date.today().year
PREPROCESSING_OBJECT_FILE_NAME="preprocessing.pkl"
SCHEMA_FILE_PATH=os.path.join('config','schema.yaml')
MODEL_FILE_PATH=os.path.join('config','model.yaml')
DATA_VALIDATION_DIR_NAME: str = "data_validation"
DATA_VALIDATION_DRIFT_REPORT_DIR: str = "drift_report"
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME: str = "report.yaml"


DATA_TRANSFORMATION_DIR_NAME: str='data_transformation'
DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR: str='transformed'
DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR:str="transformed_object"


MODEL_TRAINER_DIR_NAME:str='model_trainer'
MODEL_TRAINER_TRAINED_MODEL_DIR:str='trained_model'
MODEL_TRAINER_TRAINED_MODEL_NAME:str='model.pkl'
MODEL_TRAINER_EXCPECTED_SCORE:float=0.6
MODEL_TRAINER_MODEL_CONFIG_FILE_PATH:str=os.path.join('config','model.yaml')


