import gspread
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from oauth2client.service_account import ServiceAccountCredentials
from google.auth.transport.requests import Request
import os.path

# Define the scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# Path to your OAuth 2.0 credentials JSON file
CREDENTIALS_FILE = 'client_secret.json'

# Path to save the token file (to avoid re-authenticating every time)
TOKEN_FILE = 'token.json'


def authenticate_google_sheets():
    """Authenticate with Google Sheets API using OAuth 2.0."""
    creds = None

    # Check if a token file already exists
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If there are no valid credentials, prompt the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds


def update_google_sheet(data, sheet_name):
    """
    Updates a Google Sheet with the provided data.

    :param data: JSON or DataFrame containing the data to be uploaded.
    :param sheet_name: Name of the Google Sheet.
    """
    # Authenticate with Google Sheets API
    creds = authenticate_google_sheets()
    client = gspread.authorize(creds)

    # Create or open the Google Sheet
    try:
        sheet = client.open(sheet_name).sheet1
    except gspread.SpreadsheetNotFound:
        sheet = client.create(sheet_name).sheet1

    # Prepare the data for upload
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        df = data
    else:
        raise ValueError("Data must be a JSON object or a pandas DataFrame.")

    # Ensure the DataFrame has the required columns
    required_columns = ['Address', "Zillow_Rental_Price", "AirDNA_Revenue"]
    if not all(column in df.columns for column in required_columns):
        raise ValueError(f"DataFrame must contain the following columns: {required_columns}")

    df = df.fillna(0.0)

    # Convert DataFrame to a list of lists
    data_to_upload = [df.columns.tolist()] + df.values.tolist()

    # Update the sheet with the data
    sheet.update('A1', data_to_upload)
    print(f"Data successfully uploaded to Google Sheet: {sheet_name}")
