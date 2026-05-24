# System Architecture

## Overview

The Currency Exchange Rate Prediction System is a machine learning-powered web application developed using Django. The system collects real-time currency exchange data, processes historical trends using machine learning algorithms, and generates future exchange rate predictions through an interactive web interface.

The architecture follows a modular pipeline consisting of:

- User Interface Layer
- Django Backend Layer
- Data Collection Layer
- Machine Learning Layer
- Prediction Engine
- Visualization & Output Layer

---

# Architecture Diagram

![System Architecture](image.png)

---

# Architecture Components

## 1. User Layer

The user interacts with the application through a responsive web dashboard where currency pairs, machine learning models, and forecast duration can be selected.

### Responsibilities
- Select currency pair
- Choose ML model
- Trigger prediction
- View forecast analytics

---

## 2. Frontend Interface

The frontend is built using HTML, CSS, JavaScript, and Chart.js to provide a modern interactive dashboard.

### Features
- Interactive UI controls
- Dynamic charts
- Forecast tables
- Model comparison dashboard
- Real-time result rendering

### Technologies Used
- HTML5
- CSS3
- JavaScript
- Chart.js

---

## 3. Django Backend

The Django backend acts as the central controller of the system. It manages API requests, data flow, machine learning execution, and response generation.

### Responsibilities
- Handle frontend requests
- Process prediction APIs
- Load trained ML models
- Fetch live currency data
- Return prediction results

### Core Files
- `views.py`
- `urls.py`
- `settings.py`

---

## 4. Data Collection Module

The system fetches real-time and historical exchange rate data using Yahoo Finance APIs.

### Data Source
- Yahoo Finance API

### Functions
- Retrieve historical currency data
- Update live exchange prices
- Prepare datasets for model prediction

### File Used
- `data_fetcher.py`

---

## 5. Machine Learning Layer

This layer contains multiple regression-based machine learning models trained using historical exchange rate datasets.

### ML Models Implemented
- Linear Regression
- Ridge Regression
- Random Forest Regressor
- Gradient Boosting Regressor

### Responsibilities
- Model training
- Accuracy evaluation
- Prediction generation
- Model comparison

### File Used
- `train_model.py`

---

# Model Storage

Trained models are stored inside the `models/` directory as serialized `.pkl` files for fast loading during runtime.

Example:
- `USD_INR_linear.pkl`
- `USD_INR_random_forest.pkl`

---

## 6. Prediction Engine

The prediction engine applies trained models to processed financial data and forecasts future exchange rates.

### Functionalities
- Generate future forecasts
- Compute evaluation metrics
- Compare model performance
- Return prediction outputs

### Metrics Used
- MAE
- RMSE
- R² Score
- MAPE

---

## 7. Visualization Layer

Prediction results are displayed using interactive charts and forecast tables.

### Outputs
- Historical vs Predicted Graphs
- Forecast Tables
- Accuracy Metrics
- Model Comparison Results

---

# System Workflow

1. User selects currency pair and ML model.
2. Frontend sends request to Django backend.
3. Backend fetches live historical data from Yahoo Finance.
4. Selected machine learning model is loaded.
5. Prediction engine processes the data.
6. Forecast results are generated.
7. Metrics and visualizations are returned to frontend.
8. User views charts, tables, and prediction analytics.

---

# Deployment Architecture

The project is deployed on Render cloud hosting platform.

### Deployment Stack
- GitHub Repository
- Render Web Service
- Django Production Server

### Live Deployment
https://currency-exchange-rate-prediction-using.onrender.com/

---

# Advantages of the Architecture

- Modular system design
- Scalable backend architecture
- Multiple ML model support
- Real-time data integration
- Fast prediction response
- Interactive visualization support
- Cloud deployment ready

---

# Future Architecture Enhancements

- LSTM Deep Learning Integration
- Real-time WebSocket updates
- Docker containerization
- REST API support
- User authentication system
- Cloud database integration
- Automated model retraining pipeline

---

# Conclusion

The system architecture combines machine learning, real-time financial data processing, and Django web development into a scalable prediction platform. The modular structure ensures maintainability, extensibility, and efficient prediction performance for currency exchange forecasting applications.