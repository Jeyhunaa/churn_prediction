# 🛒 E-commerce Customer Churn Prediction

An end-to-end Machine Learning pipeline designed to identify high-risk customers using **PostgreSQL**, **XGBoost**, and **Cost-Sensitive Learning**. This project moves beyond simple model training into a structured inference engine suitable for production environments.

## 🚀 Key Features
* **SQL-to-Model Pipeline:** Automated data extraction from PostgreSQL views directly into a cleaning and scaling workflow.
* **Imbalance Handling:** Implemented **Cost-Sensitive Learning** using XGBoost's `scale_pos_weight`. This penalizes the model more heavily for missing a "Churn" case than for a "Stay" case, prioritizing **Recall** over raw Accuracy.
* **Advanced Feature Engineering:** * **Log Transformation:** Applied `log1p` to skewed features like `Tenure` to improve model convergence.
    * **Interaction Terms:** Created features like `is_unhappy_complainant` to capture complex behavioral signals.
* **Production-Ready Inference:** A dedicated `ChurnPredictor` class that ensures strict data alignment and feature symmetry between training and prediction.
* **Custom Thresholding:** Tuned the classification threshold to **0.3** to proactively identify customers at risk, even when the model is only 30-40% certain.

## 🛠️ Tech Stack
* **Database:** PostgreSQL (SQL Views for logic isolation)
* **Language:** Python 3.11+
* **Core Libraries:** Pandas, Scikit-Learn, XGBoost, Joblib
* **Environment:** Virtualenv / Pip