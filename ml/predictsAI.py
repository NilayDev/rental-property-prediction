import pandas as pd
import joblib


def predict_listings(dataframe):
    df = dataframe
    model = joblib.load("ml/model.pkl")
    X = df[['Zillow_Rental_Price', 'AirDNA_Revenue']].values
    predictions = model.predict(X)
    df["is_profitable"] = predictions.astype(bool)
    return df
