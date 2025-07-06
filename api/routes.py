from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from config import Config
from data_loader import DataLoader
from database import get_db
from analytics import BikeSharingAnalytics
from models import BikeSharingPredictor

router = APIRouter()
data_loader = DataLoader()
analytics = BikeSharingAnalytics()
predictor = BikeSharingPredictor()


class PredictionRequest(BaseModel):
    season: int = 1  # 1-4
    month: int = 1  # 1-12
    day: int = 1  # 1-30
    weekday: int = 1  # 0-6
    hour: int = 12  # 0-23
    temp: float = 0.5
    humidity: float = 0.5
    windspeed: float = 0.5
    year: int = 1  # 0 (2011) or 1 (2012)
    holiday: int = 1  # 0 or 1
    workingday: int = 1  # 0 or 1
    weathersit: int = 1  # 1-4


@router.get("/")
async def root():
    return {
        "message": "Bike Sharing Analytics API",
        "version": Config.VERSION,
        "endpoints": {
            "load_data": "/load-data",
            "train_model": "/train-model",
            "predict": "/predict",
            "analytics": "/analytics",
            "export": "/export/{data_type}"
        }
    }


@router.post("/load-data")
async def load_data(db: Session = Depends(get_db)):
    try:
        success = data_loader.load_to_database(db)

        if success:
            return {
                "message": "Data loaded successfully",
                "status": "success"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to load data")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")


@router.get("/analytics")
async def get_analytics(db: Session = Depends(get_db)):
    try:
        result = analytics.get_analytics(db)

        if result:
            return {
                "analytics": result,
                "status": "success"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate analytics")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics: {str(e)}")


@router.get("/analytics/export")
async def get_analytics(db: Session = Depends(get_db)):
    try:
        result = analytics.export_data(db)

        if result:
            return {
                "analytics": result,
                "status": "success"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate analytics")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting analytics: {str(e)}")


@router.post("/train-model")
async def train_model(hourly: bool):
    try:
        result = predictor.train_model(
            use_hourly=hourly
        )

        if result:
            return {
                "message": "Model trained successfully",
                "status": "success",
                "metrics": result
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to train model")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training model: {str(e)}")


@router.post("/predict")
async def predict_data(request: Optional[PredictionRequest] = None):
    try:
        if request is None:
            request = PredictionRequest()

        prediction = predictor.predict(
            season=request.season,
            month=request.month,
            day=request.day,
            weekday=request.weekday,
            hour=request.hour,
            temp=request.temp,
            humidity=request.humidity,
            windspeed=request.windspeed,
            year=request.year,
            holiday=request.holiday,
            workingday=request.workingday,
            weathersit=request.weathersit
        )

        if prediction is not None:
            return {
                "prediction": max(0, round(prediction)),  # Ensure non-negative
                "input_features": request.dict(),
                "status": "success"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to make prediction")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error making prediction: {str(e)}")
