from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import Dict
import json
import csv
import os
from decimal import Decimal

from config import Config
from database import DailyData, HourlyData


class BikeSharingAnalytics:

    def __init__(self):
        self.analytics_dir = Config.ANALYTICS_PATH
        if not os.path.exists(Config.ANALYTICS_PATH):
            os.makedirs(Config.ANALYTICS_PATH)

    def _save_to_csv(self, data: Dict, filename: str):
        try:
            filepath = os.path.join(self.analytics_dir, f"{filename}.csv")

            if not data:
                return

            rows = []
            for key, value in data.items():
                if isinstance(value, dict):
                    row = {'category': key}
                    row.update(value)
                    rows.append(row)
                else:
                    rows.append({'category': key, 'value': value})

            if rows:
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = rows[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
                print(f"Data saved to {filepath}")

        except Exception as e:
            print(f"Error saving {filename} to CSV: {e}")

    def get_basic_statistics(self, db: Session, save_csv: bool = False) -> Dict:
        try:
            daily_stats = db.query(
                func.count(DailyData.instant).label('total_days'),  # number of days
                func.avg(DailyData.cnt).label('avg_daily_rentals'),  # avg rentals
                func.max(DailyData.cnt).label('max_daily_rentals'),  # max num of rentals
                func.min(DailyData.cnt).label('min_daily_rentals'),  # min num of rentals
            ).first()

            hourly_stats = db.query(
                func.count(HourlyData.instant).label('total_hours'),  # number of hours
                func.avg(HourlyData.cnt).label('avg_hourly_rentals'),  # avg rentals /per hour
                func.max(HourlyData.cnt).label('max_hourly_rentals'),  # max num of rentals
                func.min(HourlyData.cnt).label('min_hourly_rentals')  # min num of rentals
            ).first()

            result = {
                'daily': {
                    'total_days': daily_stats.total_days or 0,
                    'avg_daily_rentals': round(daily_stats.avg_daily_rentals or 0, 2),
                    'max_daily_rentals': daily_stats.max_daily_rentals or 0,
                    'min_daily_rentals': daily_stats.min_daily_rentals or 0,
                },
                'hourly': {
                    'total_hours': hourly_stats.total_hours or 0,
                    'avg_hourly_rentals': round(hourly_stats.avg_hourly_rentals or 0, 2),
                    'max_hourly_rentals': hourly_stats.max_hourly_rentals or 0,
                    'min_hourly_rentals': hourly_stats.min_hourly_rentals or 0
                }
            }

            if save_csv:
                self._save_to_csv(result, 'basic_statistics')

            return result
        except Exception as e:
            print(f"Error getting basic statistics: {e}")
            return {}

    def get_seasonal_statistics(self, db: Session, save_csv: bool = False) -> Dict:
        try:
            seasonal_stats = db.query(
                DailyData.season,
                func.avg(DailyData.cnt).label('avg_rentals'),
                func.sum(DailyData.cnt).label('total_rentals'),
                func.count(DailyData.instant).label('days_count')
            ).group_by(DailyData.season).all()

            season_names = {1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'}

            result = {}
            for stat in seasonal_stats:
                season_name = season_names.get(stat.season, f'Season {stat.season}')
                result[season_name] = {
                    'avg_rentals': round(stat.avg_rentals, 2),
                    'total_rentals': stat.total_rentals,
                    'days_count': stat.days_count
                }

            if save_csv:
                self._save_to_csv(result, 'seasonal_statistics')

            return result
        except Exception as e:
            print(f"Error getting seasonal statistics: {e}")
            return {}

    def get_hourly_statistics(self, db: Session, save_csv: bool = False) -> Dict:
        try:
            hourly_stats = db.query(
                HourlyData.hr,
                func.avg(HourlyData.cnt).label('avg_rentals'),
                func.sum(HourlyData.cnt).label('total_rentals'),
                func.count(HourlyData.instant).label('hours_count')
            ).group_by(HourlyData.hr).order_by(HourlyData.hr).all()

            result = {}
            for stat in hourly_stats:
                result[f'hour_{stat.hr}'] = {
                    'avg_total_rentals': round(stat.avg_rentals, 2),
                    'total_rentals': stat.total_rentals,
                    'days_count': stat.hours_count,
                }

            if save_csv:
                self._save_to_csv(result, 'hourly_statistics')

            return result
        except Exception as e:
            print(f"Error getting hourly patterns: {e}")
            return {}

    def get_weather_impact(self, db: Session, save_csv: bool = False) -> Dict:
        try:
            weather_stats = db.query(
                DailyData.weathersit,
                func.avg(DailyData.cnt).label('avg_rentals'),
                func.count(DailyData.instant).label('days_count')
            ).group_by(DailyData.weathersit).all()

            weather_descriptions = {
                1: 'Clear/Partly Cloudy',
                2: 'Misty/Cloudy',
                3: 'Light Rain/Snow',
                4: 'Heavy Rain/Snow'
            }

            result = {}
            for stat in weather_stats:
                weather_desc = weather_descriptions.get(stat.weathersit, f'Weather {stat.weathersit}')
                result[weather_desc] = {
                    'avg_rentals': round(stat.avg_rentals, 2),
                    'days_count': stat.days_count
                }

            if save_csv:
                self._save_to_csv(result, 'weather_impact')

            return result
        except Exception as e:
            print(f"Error getting weather impact: {e}")
            return {}

    def get_monthly_trends(self, db: Session, save_csv: bool = False) -> Dict:
        try:
            monthly_stats = db.query(
                DailyData.mnth,
                func.avg(DailyData.cnt).label('avg_rentals'),
                func.sum(DailyData.cnt).label('total_rentals')
            ).group_by(DailyData.mnth).order_by(DailyData.mnth).all()

            month_names = {
                1: 'January', 2: 'February', 3: 'March', 4: 'April',
                5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'September', 10: 'October', 11: 'November', 12: 'December'
            }

            result = {}
            for stat in monthly_stats:
                month_name = month_names.get(stat.mnth, f'Month {stat.mnth}')
                result[month_name] = {
                    'avg_rentals': round(stat.avg_rentals, 2),
                    'total_rentals': stat.total_rentals
                }

            if save_csv:
                self._save_to_csv(result, 'monthly_trends')

            return result
        except Exception as e:
            print(f"Error getting monthly trends: {e}")
            return {}

    def get_weekday_patterns(self, db: Session, save_csv: bool = False) -> Dict:
        try:
            weekday_stats = db.query(
                DailyData.weekday,
                func.avg(DailyData.cnt).label('avg_rentals'),
                func.avg(DailyData.casual).label('avg_casual'),
                func.avg(DailyData.registered).label('avg_registered')
            ).group_by(DailyData.weekday).order_by(DailyData.weekday).all()

            weekday_names = {
                0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday',
                4: 'Thursday', 5: 'Friday', 6: 'Saturday'
            }

            result = {}
            for stat in weekday_stats:
                day_name = weekday_names.get(stat.weekday, f'Day {stat.weekday}')
                result[day_name] = {
                    'avg_total_rentals': round(stat.avg_rentals, 2),
                    'avg_casual_rentals': round(stat.avg_casual, 2),
                    'avg_registered_rentals': round(stat.avg_registered, 2)
                }

            if save_csv:
                self._save_to_csv(result, 'weekday_patterns')

            return result
        except Exception as e:
            print(f"Error getting weekday patterns: {e}")
            return {}

    def get_temperature_analysis(self, db: Session, save_csv: bool = False) -> Dict:
        try:
            temp_ranges = db.query(
                DailyData.temp,
                DailyData.cnt,
                case(
                    (DailyData.temp < 0.3, 'Cold'),
                    (DailyData.temp < 0.6, 'Moderate'),
                    (DailyData.temp < 0.8, 'Warm'),
                    else_='Hot'
                ).label('temp_range')
            ).subquery()

            temp_stats = db.query(
                temp_ranges.c.temp_range,  # .c = columns of subquery -> .c.temp_range
                func.avg(temp_ranges.c.cnt).label('avg_rentals'),
                func.count(temp_ranges.c.temp_range).label('days_count')
            ).group_by(temp_ranges.c.temp_range).all()

            result = {}
            for stat in temp_stats:
                result[stat.temp_range] = {
                    'avg_rentals': round(stat.avg_rentals, 2),
                    'days_count': stat.days_count
                }

            if save_csv:
                self._save_to_csv(result, 'temperature_analysis')

            return result
        except Exception as e:
            print(f"Error getting temperature analysis: {e}")
            return {}

    def get_user_type_analysis(self, db: Session, save_csv: bool = False) -> Dict:
        try:
            daily_user_stats = db.query(
                func.avg(DailyData.casual).label('avg_casual'),
                func.avg(DailyData.registered).label('avg_registered'),
                func.sum(DailyData.casual).label('total_casual'),
                func.sum(DailyData.registered).label('total_registered')
            ).first()

            hourly_user_stats = db.query(
                func.avg(HourlyData.casual).label('avg_casual'),
                func.avg(HourlyData.registered).label('avg_registered'),
                func.sum(HourlyData.casual).label('total_casual'),
                func.sum(HourlyData.registered).label('total_registered')
            ).first()

            result = {
                'daily': {
                    'avg_casual': round(daily_user_stats.avg_casual or 0, 2),
                    'avg_registered': round(daily_user_stats.avg_registered or 0, 2),
                    'total_casual': daily_user_stats.total_casual or 0,
                    'total_registered': daily_user_stats.total_registered or 0,
                },
                'hourly': {
                    'avg_casual': round(hourly_user_stats.avg_casual or 0, 2),
                    'avg_registered': round(hourly_user_stats.avg_registered or 0, 2),
                    'total_casual': hourly_user_stats.total_casual or 0,
                    'total_registered': hourly_user_stats.total_registered or 0,
                }
            }

            if save_csv:
                self._save_to_csv(result, 'user_type_analysis')

            return result
        except Exception as e:
            print(f"Error getting user type analysis: {e}")
            return {}

    def get_analytics(self, db: Session, save_csv_options: bool = False) -> Dict:

        return {
            'basic_statistics': self.get_basic_statistics(db, save_csv_options),
            'seasonal_analysis': self.get_seasonal_statistics(db, save_csv_options),
            'hourly_patterns': self.get_hourly_statistics(db, save_csv_options),
            'weather_impact': self.get_weather_impact(db, save_csv_options),
            'monthly_trends': self.get_monthly_trends(db, save_csv_options),
            'weekday_patterns': self.get_weekday_patterns(db, save_csv_options),
            'temperature_analysis': self.get_temperature_analysis(db,save_csv_options),
            'user_type_analysis': self.get_user_type_analysis(db, save_csv_options)
        }

    def convert_decimal_to_float(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {key: self.convert_decimal_to_float(value) for key, value in obj.items()}
        else:
            return obj

    def export_data(self, db: Session, save_csv_options: bool = True) -> Dict:
        try:
            analytics_dict = self.convert_decimal_to_float(
                self.get_analytics(db, save_csv_options)
            )

            file_path = os.path.join(Config.ANALYTICS_PATH, "analytics.json")
            with open(file_path, "w") as f:
                json.dump(analytics_dict, f, indent=4)

            return analytics_dict
        except Exception as e:
            print(f"Error exporting analytics: {e}")
            return {}
