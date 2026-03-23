import pandas as pd
import joblib
import os
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score, roc_auc_score

def train_and_evaluate():
    print("--- Starting Model Training Pipeline ---")

    # Load data
    FILE_PATH = r'data\processed\processed_churn_data.csv'
    dataset = pd.read_csv(FILE_PATH)

    y = dataset['churn']
    X = dataset.drop(columns=['churn'])

    # stratify train-test split to preserve class distribution due to imbalance
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

    # Calculate class distribution for handling imbalance
    num_negative = (y == 0).sum()
    num_positive = (y == 1).sum()

    scale_pos_weight = num_negative / num_positive



    # Define models
    models = {
        "Logistic Regression": LogisticRegression(max_iter = 5000, random_state = 42, class_weight="balanced"),
        "Random Forest": RandomForestClassifier(n_estimators = 100, random_state = 42, class_weight="balanced"),
        "XGBoost": XGBClassifier(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.05, 
            gamma=1,            
            scale_pos_weight=3.0, 
            eval_metric='aucpr', 
            random_state=42
        )
    }

    best_model = None
    best_f1 = 0
    best_model_name = ""
    
    # Training and evaluation
    print("\n--- Training & Comparison ---")

    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        # Metrics
        f1 = f1_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_prob)

        print(f"{name} F1 Score: {f1:.4f}")
        print(f"{name} ROC-AUC: {roc_auc:.4f}")

        # Check if this is the best one so far
        if f1 > best_f1:
            best_f1 = f1
            best_model = model
            best_model_name = name

    # Final Results
    print("\n" + "="*30)
    print(f"WINNER: {best_model_name}")
    print(f"F1 Score: {best_f1:.4f}")
    print("="*30)

    # Detailed report
    print(f"\nClassification Report for {best_model_name}:")
    winner_pred = best_model.predict(X_test)
    print(classification_report(y_test, winner_pred))

    # Save the Winner
    print(f"Saving {best_model_name} as the production model...")
    os.makedirs('models', exist_ok=True)
    
    joblib.dump(best_model, 'models/trained_model.pkl')
    
    print("Training pipeline complete. Best model saved.")

    import matplotlib.pyplot as plt

    # Get feature importance from XGBoost
    importance = best_model.feature_importances_
    feat_names = X.columns

    # Create a DataFrame for plotting
    fi_df = pd.DataFrame({'feature': feat_names, 'importance': importance})
    fi_df = fi_df.sort_values(by='importance', ascending=False).head(15)

    print("\nTop 10 Most Important Features:")
    print(fi_df)



if __name__ == "__main__":
    train_and_evaluate()