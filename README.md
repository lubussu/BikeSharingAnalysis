# Bike Sharing Analytics API

FastAPI application for bike sharing data analysis and prediction using machine learning. 

## Project Structure

```
bike-sharing-api/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration settings
├── database.py          # Database models and connection
├── data_loader.py       # Data download and loading utilities
├── analytics.py         # Analytics functions
├── models.py            # Machine learning predictor
├── api/
│   └── routes.py        # API route definitions
├── data/                # Downloaded dataset storage
├── models/              # Trained ML models storage
├── analytics/           # Generated analytics files
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd bike-sharing-api
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup
Open your terminal and connect to MySQL as root.
```bash
mysql -u root -p
```
Once connected, create the database:
```sql
CREATE DATABASE bike_sharing;
```

### 5. Environment Configuration

Create a `.env` file in the project root directory with your configuration:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=bike_sharing

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

## Usage

### Starting the Application

```bash
python main.py
```

## API Endpoints
You can test the endpoints using curl from a separate terminal window while the application is running.
### 1. Root
```bash
GET /
```
Returns basic info about the API.

**Example:**
```bash
curl -X GET "http://localhost:8000/"
```

### 2. Load Data
```bash
POST /load-data
```
Downloads and loads the bike sharing dataset into the database.

**Example:**
```bash
curl -X POST "http://localhost:8000/load-data"
```

### 2. Get Analytics
```bash
GET /analytics
```
Retrieves comprehensive analytics of the bike sharing data.

**Example:**
```bash
curl -X GET "http://localhost:8000/analytics"
```

### 3. Export Analytics
```bash
GET /analytics/export
```
Exports analytics data to JSON and CSV files.

**Example:**
```bash
curl -X GET "http://localhost:8000/analytics/export"
```

### 4. Train Model
```bash
POST /train-model?hourly=false
```
Trains the machine learning model for predictions.

**Parameters:**
- `hourly`: Boolean (true for hourly data, false for daily data)

**Example:**
```bash
curl -X POST "http://localhost:8000/train-model?hourly=false"
```

### 5. Make Predictions
```bash
POST /predict
```
Make bike rental predictions by providing input features in JSON format.

**Example:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "season": 1,
    "month": 6,
    "day": 15,
    "weekday": 1,
    "hour": 12,
    "temp": 0.6,
    "humidity": 0.5,
    "windspeed": 0.2,
    "year": 1,
    "holiday": 0,
    "workingday": 1,
    "weathersit": 1
  }'
```
If no data is provided, default values will be used.

## Testing the Project

### 1. Basic Test
Start the application:
```bash
python main.py
```
In a new terminal window, test the root endpoint:
```bash
curl http://localhost:8000/
```

### 2. Full Workflow Test
With the application running, open a new terminal and execute the following commands to test the complete pipeline:
```bash
# 1. Load data
curl -X POST "http://localhost:8000/load-data"

# 2. Get analytics
curl -X GET "http://localhost:8000/analytics"

# 3. Train model
curl -X POST "http://localhost:8000/train-model?hourly=false"

# 4. Make prediction
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "season": 2,
    "month": 5,
    "day": 10,
    "weekday": 2,
    "hour": 14,
    "temp": 0.7,
    "humidity": 0.6,
    "windspeed": 0.15,
    "year": 1,
    "holiday": 0,
    "workingday": 1,
    "weathersit": 1
  }'
```

## Output Files

The application generates several output files:

### Analytics Directory (`analytics/`)
- `basic_statistics.csv`: Basic statistical summaries
- `seasonal_statistics.csv`: Seasonal analysis
- `hourly_statistics.csv`: Hourly patterns
- `weather_impact.csv`: Weather impact analysis
- `monthly_trends.csv`: Monthly trends
- `weekday_patterns.csv`: Weekday analysis
- `temperature_analysis.csv`: Temperature correlation
- `user_type_analysis.csv`: User type patterns
- `analytics.json`: Complete analytics in JSON format

### Models Directory (`models/`)
- `bike_sharing_model.pkl`: Trained machine learning model


    
### Testing

Run the application and test all endpoints using the provided curl commands or the interactive API documentation at `/docs`.

