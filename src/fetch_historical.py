import os
import requests
from dotenv import load_dotenv
import time
import datetime

load_dotenv()
api_key = os.getenv("FIRMS_API_KEY")

bbox = "72.6,15.6,80.9,22.1"  # Maharashtra

end_date = datetime.date.today()
header_saved = False

# FIRMS caps each request at 5 days. To cover ~180 days (6 months),
# we need 36 chunks of 5 days each, stepping backward in time.
NUM_CHUNKS = 36
DAYS_PER_CHUNK = 5

with open("data/fires_historical.csv", "w") as outfile:
    for chunk in range(NUM_CHUNKS):
        chunk_end = end_date - datetime.timedelta(days=chunk * DAYS_PER_CHUNK)
        chunk_end_str = chunk_end.strftime("%Y-%m-%d")

        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{api_key}/VIIRS_SNPP_NRT/{bbox}/{DAYS_PER_CHUNK}/{chunk_end_str}"

        print(f"Fetching chunk {chunk+1}/{NUM_CHUNKS}, ending {chunk_end_str}...")
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                lines = response.text.strip().split("\n")
                if len(lines) > 1:
                    if not header_saved:
                        outfile.write(lines[0] + "\n")
                        header_saved = True
                    for line in lines[1:]:
                        outfile.write(line + "\n")
                    print(f"  -> {len(lines)-1} rows")
                else:
                    print("  -> no data in this window")
            else:
                print(f"  -> ERROR status {response.status_code}: {response.text[:200]}")
        except Exception as e:
            print(f"  -> request failed: {e}")

        time.sleep(5)

print("\nDone. Historical data saved to data/fires_historical.csv")