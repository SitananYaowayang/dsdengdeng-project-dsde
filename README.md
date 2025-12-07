# dsdengdeng Project

Welcome to the DSDEngDeng Project.

## Installation

Before starting, please ensure all dependencies are installed. Run the following command:

```
pip install -r requirements.txt
```
🚀 How to Run
Please follow these steps in order:

0. Data Preparation (Optional)
This step involves running the environment setup to initialize MongoDB and generate the CSV data.

Note: If the .csv file already exists in the directory, you can skip this step.

1. Start the Backend API
Run the API server first to enable data access for the frontend.

```
# Navigate to the streamlit directory
cd dsdengdeng-project-dsde/streamlit

# Run the API
python -m uvicorn api:app
(Please wait until the server indicates it is running before proceeding.)
```

2. Launch the Streamlit App
Start the frontend application.
```
# Ensure you are still in the 'dsdengdeng-project-dsde/streamlit' directory
streamlit run streamlit_app.py
```
Once running, the application should automatically open in your browser (typically at http://localhost:8501).