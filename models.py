import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

from database import DailyData, HourlyData, SessionLocal
from config import Config


class BikeSharingPredictor:
    def __init__(self):
        self.model = None
    def load_data_from_db(self, use_hourly=False):
        db = SessionLocal()
        try:
            if use_hourly:
                query = db.query(HourlyData).all()
                data = [record.to_dict() for record in query]
            else:
                query = db.query(DailyData).all()
                data = [record.to_dict() for record in query]

            df = pd.DataFrame(data)
            return df
        finally:
            db.close()

    def prepare_features(self, df):
        df['day'] = pd.to_datetime(df['dteday'], errors='coerce').dt.day
        X = df.drop(columns=['instant', 'casual', 'registered', 'dteday', 'cnt'])
        y = df['cnt']

        feature_names = X.columns.tolist()
        return X, y, feature_names

    def train_model(self, use_hourly=False):
        try:
            df = self.load_data_from_db(use_hourly)

            if df.empty:
                raise ValueError("No data available for training")

            print(f"Training with {len(df)} records")

            X, y, feature_names = self.prepare_features(df)

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)

            y_pred = self.model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, y_pred)

            print(f"Model trained successfully!")
            print(f"MSE: {mse:.2f}")
            print(f"RMSE: {rmse:.2f}")
            print(f"R²: {r2:.4f}")

            self.save_model()

            return {
                'mse': mse,
                'rmse': rmse,
                'r2': r2,
                'model_type': self.model.__class__.__name__,
            }

        except Exception as e:
            print(f"Error training model: {e}")
            return None

    def save_model(self):
        try:
            if os.path.exists(Config.MODEL_PATH):
                os.remove(Config.MODEL_PATH)
                print(f"Removed existing model: {Config.MODEL_PATH}")

            joblib.dump(self.model, Config.MODEL_PATH)

            print("Model saved successfully")
        except Exception as e:
            print(f"Error saving model: {e}")

    def load_model(self):
        try:
            if os.path.exists(Config.MODEL_PATH):
                self.model = joblib.load(Config.MODEL_PATH)
                return True
            else:
                print("Model files not found")
                return False
        except Exception as e:
            print(f"Error loading model: {e}")
            return False


    def predict(self, season=1, month=1, day=1, weekday=1, hour=12,
                temp=0.5, humidity=0.5, windspeed=0.2,
                year=1, holiday=0, workingday=1, weathersit=1):
        features = {
            'season': season,
            'yr': year,
            'mnth': month,
            'hr': hour,
            'holiday': holiday,
            'weekday': weekday,
            'workingday': workingday,
            'weathersit': weathersit,
            'temp': temp,
            'atemp': temp,
            'hum': humidity,
            'windspeed': windspeed,
            'day': day,
        }

        try:
            if self.model is None:
                if not self.load_model():
                    raise ValueError("Model not trained or loaded")


            if isinstance(features, dict):
                features = pd.DataFrame([features])

            prediction = self.model.predict(features)

            return prediction[0] if len(prediction) == 1 else prediction

        except Exception as e:
            print(f"Error making prediction: {e}")
            return None
