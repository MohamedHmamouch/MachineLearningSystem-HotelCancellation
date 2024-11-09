import sys

from hotel_cancellation.cloud_storage.aws_storage import SimpleStorageService
from hotel_cancellation.exception import HotelCancellationException
from hotel_cancellation.logger import logging
from hotel_cancellation.entity.artifact_entity import ModelPusherArtifact,ModelEvaluationArtifact
from hotel_cancellation.entity.config_entity import ModelPusherConfig
from hotel_cancellation.entity.S3_estimator import HotelCancellationEstimator


class ModelPusher:

    def __init__(self,
                 model_evaluation_artifact:ModelEvaluationArtifact,
                 model_pusher_config:ModelPusherConfig):
        

        self.s3=SimpleStorageService()
        self.model_evaluation_artifact=model_evaluation_artifact
        self.model_pusher_config=model_pusher_config
        self.hotel_cancellation_estimator=HotelCancellationEstimator(
            bucket_name=model_pusher_config.bucket_name,
            model_path=model_pusher_config.s3_model_key_path
        )


    

    def initiate_model_pusher(self)->ModelPusherArtifact:

        try:

            logging.info('Uploading artifacts folder to s3-bucket')

            self.hotel_cancellation_estimator.save_model(from_file=self.model_evaluation_artifact.trained_model_path)

            model_pusher_artifact=ModelPusherArtifact(bucket_name=self.model_pusher_config.bucket_name,
                                                      s3_model_path=self.model_pusher_config.s3_model_key_path)
            
            logging.info('Uploaded artifact folder to S3')
            logging.info(f"Model pusher artifact:[{model_pusher_artifact}]")
            logging.info("Exited intitiat_model_pusher of ModelTrainer class")

            return model_pusher_artifact
        

        except Exception as e:

            raise HotelCancellationException(e,sys) from e
         