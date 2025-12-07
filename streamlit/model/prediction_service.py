# model/prediction_service.py

import joblib
import pandas as pd
import numpy as np
import os

class CondoPricePredictor:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)

        model_path = os.path.join(current_dir, 'xgboost_condo_price_model.pkl')
        imputer_path = os.path.join(current_dir, 'imputer_values.pkl')
        # Ensure this points to the correct CSV location
        csv_path = os.path.join(root_dir, 'district_summary.csv') 

        try:
            self.model = joblib.load(model_path)
            self.imputer_values = joblib.load(imputer_path)
            self.df_scores = pd.read_csv(csv_path)
            
            # --- SETUP MAPS ---
            if 'district' in self.df_scores.columns:
                self.df_scores.set_index('district', inplace=True)
                
                # 1. Livability Map
                # Check for both possible column names to be safe
                if 'Livability_Score' in self.df_scores.columns:
                    self.score_map = self.df_scores['Livability_Score'].to_dict()
                elif 'Livability_Score_10' in self.df_scores.columns:
                    self.score_map = self.df_scores['Livability_Score_10'].to_dict()
                else:
                    self.score_map = {}

                # 2. Severity Map & Calculation
                if 'Avg_Severity' in self.df_scores.columns:
                    self.severity_map = self.df_scores['Avg_Severity'].to_dict()
                    # --- FIX: Define mean_severity here ---
                    self.mean_severity = self.df_scores['Avg_Severity'].mean()
                else:
                    self.severity_map = {}
                    self.mean_severity = 0 # Fallback default
            else:
                self.score_map = {}
                self.severity_map = {}
                self.mean_severity = 0
        
        except Exception as e:
            raise FileNotFoundError(f"❌ Error loading model files: {e}")
    
    def get_district_features(self, district_name):
        clean_name = str(district_name).strip()
        
        # Get Livability
        livability = self.score_map.get(clean_name, self.imputer_values.get('livability_mean', 0))
        
        # Get Severity (Now safe because self.mean_severity is defined)
        severity = self.severity_map.get(clean_name, self.mean_severity)
        
        return livability, severity
    
    def predict(self, usable_area, bedroom, restroom, district_name):
        # A. Get District Data
        livability_score, severity_score = self.get_district_features(district_name)

        # B. Handle missing user inputs
        area_final = usable_area if usable_area > 0 else self.imputer_values.get('usable_area_mean', 35)
        bed_final = bedroom if bedroom >= 0 else self.imputer_values.get('bedroom_mean', 1)
        bath_final = restroom if restroom >= 0 else self.imputer_values.get('restroom_mean', 1)
        
        # C. Create Input Array
        input_data = np.array([[
            float(area_final),
            float(bed_final),
            float(bath_final),
            float(livability_score),
            float(severity_score) 
        ]])
        
        # D. Predict
        predicted_price = self.model.predict(input_data)[0]
        
        return round(predicted_price, 2)