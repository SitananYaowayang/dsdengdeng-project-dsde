# dsdengdeng Project

Welcome to the dsdendeng Project.
2110403 Data Science and Data Engineering (DSDE-CEDT) 2025

## Installation

Before starting, please ensure all dependencies are installed. Run the following command:

```
pip install -r requirements.txt
```
## How to Run
Please follow these steps in order:

## 1. Start the Backend API
Run the API server first to enable data access for the frontend.

```
# Navigate to the streamlit directory
cd dsdengdeng-project-dsde/streamlit

# Run the API
python -m uvicorn api:app
```
(Please wait until the server indicates it is running before proceeding.)

## 2. Launch the Streamlit App
Start the frontend application.
```
# Ensure you are still in the 'dsdengdeng-project-dsde/streamlit' directory
streamlit run streamlit_app.py
```
Once running, the application should automatically open in your browser (typically at http://localhost:8501).