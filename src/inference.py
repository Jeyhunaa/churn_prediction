import pandas as pd
import numpy as np
import joblib

class ChurnPredictor:
    def __init__(self):
        try:
            self.model = joblib.load('models/trained_model.pkl')
            self.scaler = joblib.load('models/scaler.pkl')
            self.model_features = joblib.load('models/model_features.pkl')
            print("--- All model artifacts loaded successfully ---")
        except Exception as e:
            print(f"Error loading artifacts: {e}")
            raise

    def preprocess_raw_input(self, raw_data):
            df = pd.DataFrame([raw_data])
            
            # 1. FEATURE ENGINEERING (Must match preprocessing exactly)
            # Log transform tenure as we did in the new preprocessing.py
            df['tenure'] = np.log1p(df['tenure'])
            
            df['cashbackperorder'] = df['cashbackamount'] / (df['ordercount'] + 1)
            df['is_unhappy_complainant'] = ((df['complain'] == 1) & (df['satisfactionscore'] < 3)).astype(int)
            
            # Note: If you dropped 'tenure_inactivity_ratio' in preprocessing, 
            # do not calculate or use it here.

            # 2. DEFINE NUMERICAL FEATURES (Must match the Scaler's training list)
            # We removed 'hourspendonapp' and 'tenure_inactivity_ratio' to match your fix
            numerical_features = [
                    'tenure', 'warehousetohome', 
                    'orderamounthikefromlastyear', 'couponused', 
                    'ordercount', 'daysincelastorder', 'cashbackamount', 
                    'cashbackperorder'
                ]

            # 3. ENCODING
            categorical_cols = ['preferredlogindevice', 'preferredpaymentmode', 
                                'gender', 'preferedordercat', 'maritalstatus']
            df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=False)

            # 4. ALIGNMENT (Ensuring every column the model expects exists)
            # This creates a DataFrame with all 0s for missing columns
            for col in self.model_features:
                if col not in df_encoded.columns:
                    df_encoded[col] = 0
            
            # 5. FINAL REORDERING
            df_final = df_encoded[self.model_features].copy()

            # 6. SCALING
            # Now we only scale the columns that exist in our list and the scaler
            df_final[numerical_features] = self.scaler.transform(df_final[numerical_features])

            return df_final

    def predict(self, raw_input_dict):
        processed_df = self.preprocess_raw_input(raw_input_dict)
        
        # XGBoost bəzən DataFrame qəbul edərkən sütun adı xətası verir, ona görə .values istifadə edirik
        probability = self.model.predict_proba(processed_df.values)[0][1]
        
        prediction = 1 if probability > 0.3 else 0
        
        return {
            "prediction": "Churn" if prediction == 1 else "Stay",
            "probability": f"{round(probability * 100, 2)}%",
            "risk_score": round(float(probability), 4)
        }
    
# --- Quick Test ---
if __name__ == "__main__":
    predictor = ChurnPredictor()
    
    # Example: A high-risk customer profile (Low tenure, high complaints)
    sample_customer = {
        'tenure': 0.0,
        'warehousetohome': 15.0,
        'hourspendonapp': 3.0,
        'orderamounthikefromlastyear': 12.0,
        'couponused': 1.0,
        'ordercount': 1.0,
        'daysincelastorder': 5.0,
        'cashbackamount': 0.0,
        'complain': 1,
        'satisfactionscore': 1,
        'preferredlogindevice': 'Mobile Phone',
        'preferredpaymentmode': 'Debit Card',
        'gender': 'Female',
        'preferedordercat': 'Mobile Phone',
        'maritalstatus': 'Single'
    }
    
    result = predictor.predict(sample_customer)
    print(f"\nPrediction Result: {result}")

    