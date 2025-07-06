import pandas as pd
import os
import zipfile
import requests
from sqlalchemy.orm import Session

from database import DailyData, HourlyData, SessionLocal, create_db_tables
from config import Config


class DataLoader:
    def __init__(self):
        self.data_dir = "data"
        self.models_dir = "models"
        self.ensure_directories()

    def ensure_directories(self):
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)

    def download_dataset(self):
        try:
            zip_path = os.path.join(self.data_dir, "bike_sharing_dataset.zip")

            if not os.path.exists(zip_path):
                print("Downloading dataset...")
                response = requests.get(Config.DATASET_URL)
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                print("Dataset downloaded successfully")

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.data_dir)

            return True
        except Exception as e:
            print(f"Error downloading dataset: {e}")
            return False

    def load_csv_data(self):
        try:
            day_file = None
            hour_file = None

            for file in os.listdir(self.data_dir):
                if file.endswith('.csv'):
                    if 'day' in file.lower():
                        day_file = os.path.join(self.data_dir, file)
                    elif 'hour' in file.lower():
                        hour_file = os.path.join(self.data_dir, file)

            data = {}

            if os.path.exists(day_file):
                data['daily'] = pd.read_csv(day_file)
                print(f"Loaded daily data: {len(data['daily'])} records")

            if os.path.exists(hour_file):
                data['hourly'] = pd.read_csv(hour_file)
                print(f"Loaded hourly data: {len(data['hourly'])} records")

            return data
        except Exception as e:
            print(f"Error loading CSV data: {e}")
            return {}

    def load_to_database(self, db: Session = None):
        if db is None:
            db = SessionLocal()

        try:
            if not self.download_dataset():
                return False

            data = self.load_csv_data()
            if not data:
                return False

            create_db_tables()  # create db_tables

            if 'daily' in data:
                if 'dteday' in data['daily'].columns:
                    data['daily']['dteday'] = pd.to_datetime(data['daily']['dteday'])

                db.query(DailyData).delete()  # clear existing data

                for _, row in data['daily'].iterrows():
                    bike_record = DailyData(
                        instant=int(row.get('instant', 0)),
                        dteday=row.get('dteday'),
                        season=int(row.get('season', 0)),
                        yr=int(row.get('yr', 0)),
                        mnth=int(row.get('mnth', 0)),
                        holiday=int(row.get('holiday', 0)),
                        weekday=int(row.get('weekday', 0)),
                        workingday=int(row.get('workingday', 0)),
                        weathersit=int(row.get('weathersit', 0)),
                        temp=float(row.get('temp', 0)),
                        atemp=float(row.get('atemp', 0)),
                        hum=float(row.get('hum', 0)),
                        windspeed=float(row.get('windspeed', 0)),
                        casual=int(row.get('casual', 0)),
                        registered=int(row.get('registered', 0)),
                        cnt=int(row.get('cnt', 0))
                    )
                    db.add(bike_record)

                print(f"Loaded {len(data['daily'])} daily records to database")

            if 'hourly' in data:
                if 'dteday' in data['hourly'].columns:
                    data['hourly']['dteday'] = pd.to_datetime(data['hourly']['dteday'])

                db.query(HourlyData).delete()

                for _, row in data['hourly'].iterrows():
                    hourly_record = HourlyData(
                        instant=int(row.get('instant', 0)),
                        dteday=row.get('dteday'),
                        season=int(row.get('season', 0)),
                        yr=int(row.get('yr', 0)),
                        mnth=int(row.get('mnth', 0)),
                        hr=int(row.get('hr', 0)),
                        holiday=int(row.get('holiday', 0)),
                        weekday=int(row.get('weekday', 0)),
                        workingday=int(row.get('workingday', 0)),
                        weathersit=int(row.get('weathersit', 0)),
                        temp=float(row.get('temp', 0)),
                        atemp=float(row.get('atemp', 0)),
                        hum=float(row.get('hum', 0)),
                        windspeed=float(row.get('windspeed', 0)),
                        casual=int(row.get('casual', 0)),
                        registered=int(row.get('registered', 0)),
                        cnt=int(row.get('cnt', 0))
                    )
                    db.add(hourly_record)

                print(f"Loaded {len(data['hourly'])} hourly records to database")

            db.commit()  # apply changes
            return True

        except Exception as e:
            print(f"Error loading data to database: {e}")
            db.rollback()
            return False
        finally:
            db.close()
