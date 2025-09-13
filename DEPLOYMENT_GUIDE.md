# 🚀 Pharma Sales Forecasting App - Deployment Guide

## 🌐 Streamlit Cloud Deployment

### Prerequisites
- GitHub account
- Streamlit Cloud account (free at share.streamlit.io)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit - Pharma Sales Forecasting App"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. Set main file path: `streamlit_app.py`
5. Set app URL (optional): `pharma-sales-forecasting`
6. Click "Deploy!"

### Step 3: App Configuration
- **Main file**: `streamlit_app.py`
- **Requirements**: `requirements.txt`
- **Python version**: 3.8+

## 🔧 Local Development

### Run Locally
```bash
pip install -r requirements.txt
streamlit run src/dashboard/app.py --server.port 8501
```

### Access App
- Local: http://localhost:8501
- Streamlit Cloud: https://YOUR_APP_NAME.streamlit.app

## 📊 Features
- ✅ Sales Forecasting (ETS, SARIMAX, LightGBM)
- ✅ Inventory Planning
- ✅ Model Performance Analysis
- ✅ Download Reports
- ✅ Interactive Dashboard
- ✅ File Upload Support

## 🛠️ Troubleshooting
- Ensure all dependencies are in requirements.txt
- Check Python version compatibility
- Verify file paths in streamlit_app.py
- Monitor Streamlit Cloud logs for errors

## 📞 Support
For deployment issues, check:
1. Streamlit Cloud logs
2. GitHub repository settings
3. Requirements file format
4. File permissions
