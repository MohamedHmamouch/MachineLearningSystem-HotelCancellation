import os
import sys

from hotel_cancellation.entity.config_entity import HotelCancellationPredictorConfig
from hotel_cancellation.entity.S3_estimator import HotelCancellationEstimator
from hotel_cancellation.logger import logging
from hotel_cancellation.exception import HotelCancellationException
from hotel_cancellation.utils.main_utils import read_yaml_file

from pandas import DataFrame

class HotelCancellationData:
    def __init__(self,
                 meal,
                 country,
                 market_segment,
                 distribution_channel,
                 reserved_room_type,
                 assigned_room_type,
                 deposit_type,
                 customer_type,
                 lead_time,
                 arrival_date_week_number,
                 stays_in_weekend_nights,
                 stays_in_week_nights,
                 adults,
                 children,
                 babies,
                 is_repeated_guest,
                 previous_cancellations,
                 previous_bookings_not_canceled,
                 booking_changes,
                 days_in_waiting_list,
                 adr,
                 required_car_parking_spaces,
                 total_of_special_requests):
        """
        HotelCancellationData constructor
        Input: all features required for hotel cancellation prediction model
        """
        try:
            # Categorical attributes
            self.meal = meal
            self.country = country
            self.market_segment = market_segment
            self.distribution_channel = distribution_channel
            self.reserved_room_type = reserved_room_type
            self.assigned_room_type = assigned_room_type
            self.deposit_type = deposit_type
            self.customer_type = customer_type

            # Numerical attributes
            self.lead_time = lead_time
            self.arrival_date_week_number = arrival_date_week_number
            self.stays_in_weekend_nights = stays_in_weekend_nights
            self.stays_in_week_nights = stays_in_week_nights
            self.adults = adults
            self.children = children
            self.babies = babies
            self.is_repeated_guest = is_repeated_guest
            self.previous_cancellations = previous_cancellations
            self.previous_bookings_not_canceled = previous_bookings_not_canceled
            self.booking_changes = booking_changes
            self.days_in_waiting_list = days_in_waiting_list
            self.adr = adr
            self.required_car_parking_spaces = required_car_parking_spaces
            self.total_of_special_requests = total_of_special_requests

        except Exception as e:

            raise HotelCancellationException(e,sys) from e
        

    def get_hotelcancelllation_input_dataframe(self):

        try:

            hotelcancellation_input_dict=self.get_hotel_cancellation_data_as_dict()

            return DataFrame(hotelcancellation_input_dict)
        
        except Exception as e:

            raise HotelCancellationException(e,sys) from e
        
    
    def get_hotelcancellation_data_as_dict(self):


        try:
            input_data = {
                "meal": [self.meal],
                "country": [self.country],
                "market_segment": [self.market_segment],
                "distribution_channel": [self.distribution_channel],
                "reserved_room_type": [self.reserved_room_type],
                "assigned_room_type": [self.assigned_room_type],
                "deposit_type": [self.deposit_type],
                "customer_type": [self.customer_type],
                "lead_time": [self.lead_time],
                "arrival_date_week_number": [self.arrival_date_week_number],
                "stays_in_weekend_nights": [self.stays_in_weekend_nights],
                "stays_in_week_nights": [self.stays_in_week_nights],
                "adults": [self.adults],
                "children": [self.children],
                "babies": [self.babies],
                "is_repeated_guest": [self.is_repeated_guest],
                "previous_cancellations": [self.previous_cancellations],
                "previous_bookings_not_canceled": [self.previous_bookings_not_canceled],
                "booking_changes": [self.booking_changes],
                "days_in_waiting_list": [self.days_in_waiting_list],
                "adr": [self.adr],
                "required_car_parking_spaces": [self.required_car_parking_spaces],
                "total_of_special_requests": [self.total_of_special_requests],
            }

            logging.info('created hotelcanncellationdata as dict')

            logging.info('Exited hotel_cancellation_data_as_dict method as HotelCancellationData class')

            return input_data
        
        except Exception as e:

            raise HotelCancellationException(e,sys) from e
        

class HotelCancellationClassifier:

    def __init__(self,prediction_pipeline_config:HotelCancellationPredictorConfig=HotelCancellationPredictorConfig()):

        try:

            self.prediction_pipeline_config=prediction_pipeline_config

        except Exception as e:

            raise HotelCancellationException(e,sys)
        

    

    def predict(self,dataframe)->str:


        try:

            logging.info('Entered predict method of HotelCancellationClassifier class')

            model=HotelCancellationEstimator(
                bucket_name=self.prediction_pipeline_config.model_bucket_name,
                model_path=self.prediction_pipeline_config.model_file_path
            )

            result=model.predict(dataframe)

            return result
        
        except Exception as e:

            raise HotelCancellationException(e,sys)
        

           
