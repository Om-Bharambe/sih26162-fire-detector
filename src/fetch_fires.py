import os
import requests
from dotenv import load_dotenv

# Load the .env file so we can read the API key
load_dotenv()

api_key = os.getenv("FIRMS_API_KEY")

if not api_key:
    print("ERROR: FIRMS_API_KEY not found. Check your .env file.")
    exit()

# Bounding box roughly covering India: (west, south, east, north)
bbox = "72.6,15.6,80.9,22.1"

url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{api_key}/VIIRS_SNPP_NRT/{bbox}/5"

response = requests.get(url)

if response.status_code == 200:
    # Save the raw CSV response to a file
    with open("data/fires_raw.csv", "w") as f:
        f.write(response.text)
    print("Saved fire data to data/fires_raw.csv")
    print("Preview:")
    print(response.text[:500])
else:
    print("ERROR: Status code", response.status_code)
    print(response.text)