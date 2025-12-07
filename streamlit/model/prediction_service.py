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
        csv_path = os.path.join(root_dir, 'district_summary.csv')

        try:
            self.model = joblib.load(model_path)
            self.imputer_values = joblib.load(imputer_path)
            self.df_scores = pd.read_csv(csv_path)
            
            if 'district' in self.df_scores.columns and 'Livability_Score_10' in self.df_scores.columns:
                self.score_map = self.df_scores.set_index('district')['Livability_Score_10'].to_dict()
                # self.score_map = dict(zip(df_scores['district'], df_scores['Livability_Score_10']))
            else:
                self.score_map = {}
        
        except Exception as e:
            raise FileNotFoundError(f"❌ Error loading model files: {e}")
    
    def get_livability_score(self, district_name):
        # Convert district name to score
        # Look up in the dict (if not found, use mean value)
        return self.score_map.get(district_name, self.imputer_values['livability_mean'])

    # The price prediction function
    def predict(self, usable_area, bedroom, restroom, district_name):
        
        # A. Convert district name to livability score
        livability_score = self.get_livability_score(district_name)

        # B. Handle missing values (If the User doesn't provide a value, use the mean)
        area_final = usable_area if usable_area > 0 else self.imputer_values['usable_area_mean']
        bed_final = bedroom if bedroom >= 0 else self.imputer_values['bedroom_mean']
        bath_final = restroom if restroom >= 0 else self.imputer_values['restroom_mean']
        
        # C. Create Input Array to send to the model
        # [usable_area, bedroom, restroom, Livability_Score_10]
        input_data = np.array([[
            float(area_final),
            float(bed_final),
            float(bath_final),
            float(livability_score)
        ]])
        
        # D. Predict
        predicted_price = self.model.predict(input_data)[0]
        
        return round(predicted_price, 2)