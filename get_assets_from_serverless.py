import os
import sys
import csv
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get Twilio credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
service_sid = os.getenv("TWILIO_SERVERLESS_SERVICE_SID")

# Validate inputs
if not service_sid:
    print("Please provide TWILIO_SERVERLESS_SERVICE_SID in your .env file.")
    sys.exit(1)

client = Client(account_sid, auth_token)

def list_assets_csv():
    try:
        assets = client.serverless.v1.services(service_sid).assets.list(limit=100)

        if not assets:
            print("No assets found.")
            return

        # CSV header
        writer = csv.writer(sys.stdout)
        writer.writerow(["Asset SID", "Friendly Name"])

        # CSV rows
        for asset in assets:
            writer.writerow([
                asset.sid or "",
                asset.friendly_name or "",
            ])

    except Exception as e:
        print(f"Error fetching assets: {e}")

if __name__ == "__main__":
    list_assets_csv()