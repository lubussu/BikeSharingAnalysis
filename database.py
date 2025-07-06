from sqlalchemy import create_engine, Column, Integer, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()  # Base class for models representing database tables


class DailyData(Base):
    __tablename__ = "day"

    instant = Column(Integer, primary_key=True, index=True)
    dteday = Column(Date)
    season = Column(Integer)
    yr = Column(Integer)
    mnth = Column(Integer)
    holiday = Column(Integer)
    weekday = Column(Integer)
    workingday = Column(Integer)
    weathersit = Column(Integer)
    temp = Column(Float)
    atemp = Column(Float)
    hum = Column(Float)
    windspeed = Column(Float)
    casual = Column(Integer)
    registered = Column(Integer)
    cnt = Column(Integer)

    def to_dict(self):
        return {
            "instant": self.instant,
            "dteday": self.dteday.isoformat() if self.dteday else None,
            "season": self.season,
            "yr": self.yr,
            "mnth": self.mnth,
            "holiday": self.holiday,
            "weekday": self.weekday,
            "workingday": self.workingday,
            "weathersit": self.weathersit,
            "temp": self.temp,
            "atemp": self.atemp,
            "hum": self.hum,
            "windspeed": self.windspeed,
            "casual": self.casual,
            "registered": self.registered,
            "cnt": self.cnt
        }


class HourlyData(Base):
    __tablename__ = "hour"

    instant = Column(Integer, primary_key=True, index=True)
    dteday = Column(Date)
    season = Column(Integer)
    yr = Column(Integer)
    mnth = Column(Integer)
    hr = Column(Integer)
    holiday = Column(Integer)
    weekday = Column(Integer)
    workingday = Column(Integer)
    weathersit = Column(Integer)
    temp = Column(Float)
    atemp = Column(Float)
    hum = Column(Float)
    windspeed = Column(Float)
    casual = Column(Integer)
    registered = Column(Integer)
    cnt = Column(Integer)

    def to_dict(self):
        return {
            "instant": self.instant,
            "dteday": self.dteday.isoformat() if self.dteday else None,
            "season": self.season,
            "yr": self.yr,
            "mnth": self.mnth,
            "hr": self.hr,
            "holiday": self.holiday,
            "weekday": self.weekday,
            "workingday": self.workingday,
            "weathersit": self.weathersit,
            "temp": self.temp,
            "atemp": self.atemp,
            "hum": self.hum,
            "windspeed": self.windspeed,
            "casual": self.casual,
            "registered": self.registered,
            "cnt": self.cnt
        }


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_tables():
    Base.metadata.create_all(bind=engine)
