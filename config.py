import os
from dotenv import load_dotenv

load_dotenv()  # carica le variabili d'ambiente


class Config:
    # Database configuration
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "bike_sharing")

    # Database URL
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Paths
    MODEL_PATH = "models/bike_sharing_model.pkl"
    ANALYTICS_PATH = "analytics/"

    # Dataset configuration
    DATASET_URL = "https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip"

    # API configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))

    # App configuration
    APP_NAME = "Bike Sharing API"
    VERSION = "1.0.0"
    DESCRIPTION = "API for bike sharing data analysis and predictions"
