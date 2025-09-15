# Sales-Analysis-and-Forecasting-Pharma
Analyze historical pharma sales data and build forecasting models to predict future trends. Includes EDA, time series modeling, and visualizations for actionable insights.

# 📊 Sales Analysis and Forecasting System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

> **Advanced Machine Learning Solutions for Pharmaceutical Sales Forecasting**

A comprehensive sales analysis and forecasting system that leverages multiple machine learning models to predict pharmaceutical sales trends with high accuracy. Features an interactive Streamlit dashboard for real-time insights and model comparison.

## 🎯 Overview

This project addresses the critical challenge of accurate sales forecasting in the pharmaceutical industry by implementing a multi-model approach that combines statistical methods (ETS, SARIMA) with machine learning algorithms (LightGBM) to deliver highly accurate predictions across multiple time horizons.

### Key Features

- 🔮 **Multi-Model Forecasting**: ETS, SARIMA, LightGBM, and Ensemble methods
- 📈 **Real-time Dashboard**: Interactive Streamlit interface with live visualizations
- ⏰ **Multi-timeframe Support**: Hourly, daily, weekly, and monthly predictions
- 📊 **Advanced Analytics**: Comprehensive model comparison and performance metrics
- 🚀 **Production Ready**: Docker containerization and Heroku deployment
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Layer    │    │   ML Pipeline    │    │   Dashboard     │
│                 │    │                  │    │                 │
│ • Raw Data      │───▶│ • Preprocessing   │───▶│ • Streamlit UI  │
│ • Processed     │    │ • Feature Eng.    │    │ • Visualizations│
│ • Models        │    │ • Training       │    │ • Export        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/sales-analysis-forecasting.git
   cd sales-analysis-forecasting
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run src/dashboard/app.py --server.port 8501
   ```

4. **Access the dashboard**
   Open your browser and navigate to `http://localhost:8501`

### Alternative: Docker Deployment

```bash
# Build the Docker image
docker build -t sales-forecasting .

# Run the container
docker run -p 8501:8501 sales-forecasting
```

## 📁 Project Structure

```
sales-analysis-forecasting/
├── 📁 data/
│   ├── raw/                    # Original datasets
│   │   ├── salesdaily.xls
│   │   ├── saleshourly.xls
│   │   ├── salesmonthly.xls
│   │   └── salesweekly.xls
│   └── outputs/
│       └── trained_models/     # Saved ML models
├── 📁 src/
│   ├── dashboard/              # Streamlit dashboard
│   │   └── app.py
│   ├── data/                   # Data processing
│   │   └── ingest.py
│   ├── features/               # Feature engineering
│   │   └── build_features.py
│   ├── models/                 # ML models
│   │   ├── ets.py
│   │   ├── sarimax.py
│   │   ├── lgbm.py
│   │   └── interface.py
│   ├── evaluate/               # Model evaluation
│   │   ├── metrics.py
│   │   └── select.py
│   └── serving/                # API endpoints
│       └── api.py
├── 📁 scripts/                 # Utility scripts
├── 📄 requirements.txt         # Python dependencies
├── 📄 streamlit_app.py        # Main app entry point
└── 📄 README.md               # This file
```

## 🤖 Machine Learning Models

### 1. ETS (Exponential Smoothing)
- **Type**: Statistical time series method
- **Strengths**: Fast, interpretable, excellent for trend and seasonality
- **Use Case**: Baseline forecasting with clear patterns

### 2. SARIMA (Seasonal ARIMA)
- **Type**: Statistical model with seasonal components
- **Strengths**: Handles complex seasonal patterns effectively
- **Use Case**: Time series with strong seasonal behavior

### 3. LightGBM (Gradient Boosting)
- **Type**: Machine learning ensemble method
- **Strengths**: High accuracy, fast training, handles non-linear relationships
- **Use Case**: Complex patterns and feature interactions

### 4. Ensemble Methods
- **Type**: Combination of multiple models
- **Strengths**: Robust predictions, reduced overfitting
- **Use Case**: Final predictions with improved accuracy

## 📊 Performance Metrics

| Model | Accuracy | Speed | Interpretability | Seasonality Handling |
|-------|----------|-------|------------------|---------------------|
| ETS | Good | Fast | High | Excellent |
| SARIMA | Very Good | Medium | High | Excellent |
| LightGBM | Excellent | Fast | Medium | Good |
| Ensemble | Excellent | Medium | Low | Excellent |

## 🛠️ Technology Stack

### Frontend
- **Streamlit**: Interactive web application framework
- **Plotly**: Advanced data visualizations
- **Pandas**: Data manipulation and analysis

### Backend
- **Python 3.8+**: Core programming language
- **FastAPI**: High-performance API framework
- **NumPy**: Numerical computing

### Machine Learning
- **Scikit-learn**: Machine learning algorithms
- **LightGBM**: Gradient boosting framework
- **Statsmodels**: Statistical modeling (SARIMA/ETS)
- **Joblib**: Model persistence and caching

### Deployment
- **Docker**: Containerization
- **Heroku**: Cloud deployment platform
- **Git/GitHub**: Version control and collaboration

## 📈 Usage Examples

### Basic Forecasting
```python
from src.models.interface import ForecastingInterface

# Initialize the forecasting system
forecaster = ForecastingInterface()

# Load and preprocess data
data = forecaster.load_data('data/raw/salesdaily.xls')

# Train models
forecaster.train_models(data)

# Generate forecasts
forecasts = forecaster.predict(horizon=30)
```

### Model Comparison
```python
# Compare model performance
results = forecaster.compare_models()
print(results[['model', 'mae', 'rmse', 'mape']])
```

### Dashboard Integration
```python
# Run the interactive dashboard
import subprocess
subprocess.run(['streamlit', 'run', 'src/dashboard/app.py'])
```

## 📊 Dashboard Features

### Interactive Visualizations
- **Time Series Plots**: Zoom, pan, and analyze trends
- **Model Performance Charts**: Real-time accuracy tracking
- **Forecast Comparisons**: Side-by-side model predictions
- **Confidence Intervals**: Uncertainty quantification

### Data Management
- **File Upload**: Support for Excel/CSV data formats
- **Data Export**: Download forecasts and reports
- **Parameter Tuning**: Adjust model parameters in real-time
- **Model Persistence**: Save and load trained models

### Analytics
- **Performance Metrics**: MAE, RMSE, MAPE, WMAPE
- **Model Selection**: Automated best model identification
- **Backtesting**: Historical performance validation
- **Feature Importance**: Model interpretability insights

## 🚀 Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run src/dashboard/app.py --server.port 8501
```

### Production Deployment (Heroku)
```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-app-name

# Deploy
git push heroku main
```

### Docker Deployment
```bash
# Build image
docker build -t sales-forecasting .

# Run container
docker run -p 8501:8501 sales-forecasting
```

## 📚 API Documentation

### Endpoints

#### `/api/forecast`
- **Method**: POST
- **Description**: Generate sales forecasts
- **Parameters**: 
  - `data`: Time series data
  - `horizon`: Forecast horizon (days)
  - `model`: Model type (optional)

#### `/api/models/compare`
- **Method**: GET
- **Description**: Compare model performance
- **Returns**: Performance metrics for all models

#### `/api/models/train`
- **Method**: POST
- **Description**: Train models with new data
- **Parameters**: `data`: Training dataset

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_models.py

# Run with coverage
python -m pytest --cov=src tests/
```

### Test Coverage
- Unit tests for all model classes
- Integration tests for API endpoints
- End-to-end tests for dashboard functionality

## 📊 Datasets

### Kaggle Pharmaceutical Sales Dataset
- **Source**: [Kaggle - Pharmaceutical Sales Data](https://www.kaggle.com/datasets/pharmaceutical-sales)
- **Description**: Multi-granularity sales data for pharmaceutical products
- **Features**: 
  - Daily, weekly, monthly, and hourly sales data
  - Product categories and SKU information
  - Time series patterns and seasonality
- **Size**: Multiple files with varying time granularities

### Data Preprocessing
- **Cleaning**: Handle missing values and outliers
- **Feature Engineering**: Create lag features, rolling statistics
- **Validation**: Train/validation/test splits
- **Scaling**: Normalize features for model training

## 🔧 Configuration

### Environment Variables
```bash
# Model configuration
MODEL_CACHE_DIR=./data/outputs/trained_models
MAX_FORECAST_HORIZON=365
DEFAULT_MODEL=ensemble

# API configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# Dashboard configuration
DASHBOARD_PORT=8501
DASHBOARD_THEME=light
```

### Model Parameters
```python
# ETS parameters
ETS_PARAMS = {
    'trend': 'add',
    'seasonal': 'add',
    'seasonal_periods': 12
}

# SARIMA parameters
SARIMA_PARAMS = {
    'order': (1, 1, 1),
    'seasonal_order': (1, 1, 1, 12)
}

# LightGBM parameters
LGBM_PARAMS = {
    'n_estimators': 100,
    'learning_rate': 0.1,
    'max_depth': 6
}
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Fork the repository
git clone https://github.com/yourusername/sales-analysis-forecasting.git

# Create a feature branch
git checkout -b feature/your-feature-name

# Install development dependencies
pip install -r requirements-dev.txt

# Make your changes and test
python -m pytest tests/

# Submit a pull request
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Data Science Team**: Model development and evaluation
- **Backend Team**: API development and deployment
- **Frontend Team**: Dashboard design and user experience
- **DevOps Team**: Infrastructure and deployment automation

## 📞 Support

- **Documentation**: [Full Documentation](documentation.txt)
- **Issues**: [GitHub Issues](https://github.com/yourusername/sales-analysis-forecasting/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/sales-analysis-forecasting/discussions)
- **Email**: support@yourcompany.com

## 🙏 Acknowledgments

- **Kaggle Community**: For providing the pharmaceutical sales dataset
- **Open Source Libraries**: Scikit-learn, LightGBM, Streamlit, Plotly
- **Research Community**: Time series forecasting methodologies
- **Contributors**: All developers who contributed to this project

## 📈 Roadmap

### Version 2.0 (Q2 2024)
- [ ] Real-time data streaming integration
- [ ] Advanced deep learning models (LSTM, Transformer)
- [ ] Automated hyperparameter optimization
- [ ] Multi-tenant architecture

### Version 3.0 (Q4 2024)
- [ ] Mobile application development
- [ ] API integration with ERP systems
- [ ] Advanced analytics and reporting
- [ ] Machine learning pipeline automation

---

**⭐ Star this repository if you find it helpful!**

*Built with ❤️ for the pharmaceutical industry*


