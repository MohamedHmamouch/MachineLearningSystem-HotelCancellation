from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from uvicorn import run as app_run

from typing import Optional
from hotel_cancellation.entity.config_entity import HotelCancellationPredictorConfig
from hotel_cancellation.entity.S3_estimator import HotelCancellationEstimator
from hotel_cancellation.logger import logging
from hotel_cancellation.exception import HotelCancellationException
from hotel_cancellation.utils.main_utils import read_yaml_file
from pandas import DataFrame
from hotel_cancellation.pipline.prediction_pipeline import HotelCancellationData, HotelCancellationClassifier

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up HTML templates and CORS
templates = Jinja2Templates(directory='templates')
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define a data form handler for input fields from the form
class DataForm:
    def __init__(self, request: Request):
        self.request: Request = request
        # Define all the required fields here based on the model class
        self.meal: Optional[str] = None
        self.country: Optional[str] = None
        self.market_segment: Optional[str] = None
        self.distribution_channel: Optional[str] = None
        self.reserved_room_type: Optional[str] = None
        self.assigned_room_type: Optional[str] = None
        self.deposit_type: Optional[str] = None
        self.customer_type: Optional[str] = None
        self.lead_time: Optional[int] = None
        self.arrival_date_week_number: Optional[int] = None
        self.stays_in_weekend_nights: Optional[int] = None
        self.stays_in_week_nights: Optional[int] = None
        self.adults: Optional[int] = None
        self.children: Optional[int] = None
        self.babies: Optional[int] = None
        self.is_repeated_guest: Optional[int] = None
        self.previous_cancellations: Optional[int] = None
        self.previous_bookings_not_canceled: Optional[int] = None
        self.booking_changes: Optional[int] = None
        self.days_in_waiting_list: Optional[int] = None
        self.adr: Optional[float] = None
        self.required_car_parking_spaces: Optional[int] = None
        self.total_of_special_requests: Optional[int] = None
        
    async def get_hotel_cancellation_data(self):
        form = await self.request.form()
        
        self.meal = form.get("meal")
        self.country = form.get("country")
        self.market_segment = form.get("market_segment")
        self.distribution_channel = form.get("distribution_channel")
        self.reserved_room_type = form.get("reserved_room_type")
        self.assigned_room_type = form.get("assigned_room_type")
        self.deposit_type = form.get("deposit_type")
        self.customer_type = form.get("customer_type")
        self.lead_time = int(form.get("lead_time", 0))
        self.arrival_date_week_number = int(form.get("arrival_date_week_number", 0))
        self.stays_in_weekend_nights = int(form.get("stays_in_weekend_nights", 0))
        self.stays_in_week_nights = int(form.get("stays_in_week_nights", 0))
        self.adults = int(form.get("adults", 0))
        self.children = int(form.get("children", 0))
        self.babies = int(form.get("babies", 0))
        self.is_repeated_guest = int(form.get("is_repeated_guest", 0))
        self.previous_cancellations = int(form.get("previous_cancellations", 0))
        self.previous_bookings_not_canceled = int(form.get("previous_bookings_not_canceled", 0))
        self.booking_changes = int(form.get("booking_changes", 0))
        self.days_in_waiting_list = int(form.get("days_in_waiting_list", 0))
        self.adr = float(form.get("adr", 0.0))
        self.required_car_parking_spaces = int(form.get("required_car_parking_spaces", 0))
        self.total_of_special_requests = int(form.get("total_of_special_requests", 0))

@app.get("/", tags=["hotel_cancellation"])
async def index(request: Request):
    return templates.TemplateResponse("hotel_cancellation.html", {"request": request, "context": "Rendering"})

@app.post("/predict")
async def predict(request: Request):
    try:
        form = DataForm(request)
        await form.get_hotel_cancellation_data()

        hotel_cancellation_data = HotelCancellationData(
            meal=form.meal,
            country=form.country,
            market_segment=form.market_segment,
            distribution_channel=form.distribution_channel,
            reserved_room_type=form.reserved_room_type,
            assigned_room_type=form.assigned_room_type,
            deposit_type=form.deposit_type,
            customer_type=form.customer_type,
            lead_time=form.lead_time,
            arrival_date_week_number=form.arrival_date_week_number,
            stays_in_weekend_nights=form.stays_in_weekend_nights,
            stays_in_week_nights=form.stays_in_week_nights,
            adults=form.adults,
            children=form.children,
            babies=form.babies,
            is_repeated_guest=form.is_repeated_guest,
            previous_cancellations=form.previous_cancellations,
            previous_bookings_not_canceled=form.previous_bookings_not_canceled,
            booking_changes=form.booking_changes,
            days_in_waiting_list=form.days_in_waiting_list,
            adr=form.adr,
            required_car_parking_spaces=form.required_car_parking_spaces,
            total_of_special_requests=form.total_of_special_requests
        )

        hotel_cancellation_df = hotel_cancellation_data.get_hotelcancelllation_input_dataframe()


        classifier = HotelCancellationClassifier()
        prediction = classifier.predict(hotel_cancellation_df)

        status = "Cancellation Likely" if prediction == 1 else "Cancellation Unlikely"

        return templates.TemplateResponse("hotel_cancellation.html", {"request": request, "context": status})

    except Exception as e:
        return {"status": False, "error": f"{e}"}

if __name__ == "__main__":
    app_run(app, host="127.0.0.1", port=8000)
