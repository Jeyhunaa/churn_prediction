import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
import joblib  
import os

# 1. Database Connection
engine = create_engine('postgresql+psycopg2://postgres:admin@localhost:5432/postgres')

def process_data():
    # Load data from the SQL View
    query = "SELECT * FROM v_ecommerce_cleaned"
    df = pd.read_sql(query, engine)
    df.columns = df.columns.str.lower().str.strip()
    
    # --- QUALITY CONTROL STEPS ---
    
    # A. Handling Duplicates
    df = df.drop_duplicates(subset=['customerid'], keep='first')
    
    # B. Imputation
    cols_to_impute = ['tenure', 'warehousetohome', 'hourspendonapp', 
                      'orderamounthikefromlastyear', 'couponused', 
                      'ordercount', 'daysincelastorder']
    for col in cols_to_impute:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # C. Outlier Treatment (Capping at 1st and 99th Percentile)
    cols_with_outliers = ['warehousetohome', 'cashbackamount', 'tenure']
    for col in cols_with_outliers:
        lower_cap = df[col].quantile(0.01)
        upper_cap = df[col].quantile(0.99)
        df[col] = np.clip(df[col], lower_cap, upper_cap)

    # --- FEATURE ENGINEERING ---
    
    df['tenure'] = np.log1p(df['tenure']) 
    df['cashbackperorder'] = df['cashbackamount'] / (df['ordercount'] + 1)
    df['is_unhappy_complainant'] = ((df['complain'] == 1) & (df['satisfactionscore'] < 3)).astype(int)

    # --- ENCODING & SCALING ---

    # D. Encoding (Categorical to Numerical)
    categorical_cols = ['preferredlogindevice', 'preferredpaymentmode', 
                        'gender', 'preferedordercat', 'maritalstatus']
    df_final = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
    
    df_final = df_final.drop(columns=['customerid'])

    # E. Scaling (Standardizing numerical features)
    # Important: Scale ONLY the continuous numbers, not the 0/1 dummies
    numerical_features = [
        'tenure', 'warehousetohome', 
        'orderamounthikefromlastyear', 'couponused', 
        'ordercount', 'daysincelastorder', 'cashbackamount', 
        'cashbackperorder'
    ]
    
    scaler = StandardScaler()
    df_final[numerical_features] = scaler.fit_transform(df_final[numerical_features])


    cols_to_drop = ['citytier', 'hourspendonapp', 'numberofdeviceregistered', 'customerid']
    df_final = df_final.drop(columns=[c for c in cols_to_drop if c in df_final.columns], errors='ignore')

    # Save the Scaler
    joblib.dump(scaler, 'models/scaler.pkl')
    
    # Save the final column list (excluding the target 'churn')
    # This ensures your API always sends columns in the right order
    model_features = [col for col in df_final.columns if col != 'churn']
    joblib.dump(model_features, 'models/model_features.pkl')
    
    print("Success: Scaler and Feature List saved to /models")


    # --- EXPORT ---
    output_dir = os.path.join('data', 'processed')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, 'processed_churn_data.csv')
    df_final.to_csv(output_path, index=False)
    
    print(f"Full preprocessing complete. Cleaned and Scaled data saved to: {output_path}")
    return df_final

if __name__ == "__main__":
    process_data()