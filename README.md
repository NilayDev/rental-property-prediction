# Flask Real Estate Rental Listing Project README

## Prerequisites
Ensure you have the following installed:
- Python 3.x
- pip (Python package manager)
- Virtual environment (optional but recommended)

## Installation
1. **Clone the repository**
   ```sh
   git clone <repository_url>
   cd <project_directory>
   ```
2. **Intall Virtualenv**
    ```sh
    sudo apt-get install python3-venv   # On macOS/Linux
    pip install virtualenv   # On Windows
    
2. **Create a virtual environment (optional but recommended)**
   ```sh
   python -m venv venv  # On Windows
   python3 -m venv venv  # On macOS/Linux
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate  # On Windows
   ```
3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```


## Running the Application
**Run the Flask application**
   ```sh
   flask run
   ```
   The app will be available at `http://127.0.0.1:5000/`


## Test 2x Data Projection Endpoint
**steps**

1. **Test the endpoint with any of the below method.**
   ```sh
   http://127.0.0.1:5000/process   # Use this endpoint with post request.
   curl --location --request POST 'http://127.0.0.1:5000/process'   # Test with this curl command in terminal.
   ```

## Current Workflow
- In the data folder, we have a zillow_data.csv in which we added sample addresses scraped from Zillow.com.
- Also, in the scrapping directory we've added a scrape_zillow.py file which could run independently to scrape rental properties data from zillow and store it in the data directory.
- We are taking address from zillow_data.csv and scrape the respective projected revenues from app.airdna.co.
- After getting record from airdna we are comparing the record prices from zillow and airdna using AI model trained for RandomForest Classification technique and getting if that property is projected 2x rent price or not.
- After we get all address record we are adding final data to google spread sheet.
- We will get spreadsheet name in response in above process endpoint.
- Also we are storing predicted output in prediction_data csv in data folder.