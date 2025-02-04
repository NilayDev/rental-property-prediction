from flask import Flask, jsonify
import pandas as pd
import re
import logging
from dotenv import load_dotenv

from helpers.google_sheets import update_google_sheet
from ml.predictsAI import predict_listings
from scraping.airdna_service import get_projected_revenue

app = Flask(__name__)

load_dotenv()

logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define file paths
ZILLOW_CSV = "data/zillow_data.csv"
MERGED_CSV = "data/merged_real_estate_data.csv"


def clean_zillow_price(price_str):
    """
    Convert Zillow price string from '$3,340/mo' to annual rent (e.g., 3340 * 12 = 40080).

    :param price_str: str, raw price string from Zillow (e.g., "$3,340/mo", "Price Unknown")
    :return: int or None, annual rent price (e.g., 40080) or None if invalid
    """
    if not price_str or "Price Unknown" in price_str:
        return None  # Handle unknown or missing values

    # Extract numerical value from string
    price_str = re.sub(r"[^\d]", "", price_str)  # Remove non-numeric characters
    try:
        return int(price_str)
    except ValueError:
        return None  # Handle unexpected format


def load_zillow_data():
    """
    Load Zillow data and convert rent price to yearly format.

    :param file_path: str, path to Zillow CSV file
    :return: DataFrame, cleaned Zillow data with yearly rent prices
    """
    df = pd.read_csv(ZILLOW_CSV)

    df = df[df["price"] != "Price Unknown"]

    # Convert Zillow monthly rent to annual rent
    df.drop_duplicates(inplace=True)
    df["price"] = df["price"].apply(clean_zillow_price)
    df["address"] = df["address"].str.lower().str.strip()

    return df  # Keep only necessary columns


def merge_data(zillow_df, airdna_data):
    """ Merge Zillow and AirDNA data using direct address matching """
    merged_list = []

    for index, row in zillow_df.iterrows():
        address = row["address"]
        if address in airdna_data:
            merged_list.append({
                "Address": address,
                "Zillow_Rental_Price": row["price"],
                "AirDNA_Revenue": airdna_data[address]
            })

    return pd.DataFrame(merged_list)


@app.route("/process", methods=["GET"])
def process_data():
    """ Run the full pipeline: Scrape AirDNA, merge data, and save CSV """

    # 1. Load Zillow data
    logging.info("Fetching rental listings from zillow.com")
    zillow_df = load_zillow_data()
    addresses = zillow_df["address"].tolist()

    # 2. Get projected revenue from AirDNA
    logging.info("Fetching projected revenues from airdna.com")
    airdna_data = get_projected_revenue(addresses)

    # 3. Merge Zillow & AirDNA data
    logging.info("Merging Zillow data with the projected revenues from AirDNA")
    merged_df = merge_data(zillow_df, airdna_data)
    merged_df.to_csv("data/merged_data.csv")

    logging.info("Predicting the merged data...")
    ai_prediction = predict_listings(merged_df)

    logging.info("Updating the predicted data to google sheet")
    update_google_sheet(ai_prediction, "Rental Properties")

    return {"message": "Merged data saved successfully!", "file": MERGED_CSV}


if __name__ == "__main__":
    app.run(debug=True)
