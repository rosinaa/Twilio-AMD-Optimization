import os
import json
import time
import sys
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
FROM_NUMBER = os.getenv('OUTBOUND_PHONE_NUMBER')
TO_NUMBER = os.getenv('INBOUND_PHONE_NUMBER')

assert ACCOUNT_SID and AUTH_TOKEN and FROM_NUMBER and TO_NUMBER, "Please check your .env configuration."

CONFIG_FILE = "amd_config.json"

def load_config(filename):
    with open(filename, "r") as f:
        return json.load(f)

def build_call_kwargs(config):
    return {
        "from_": FROM_NUMBER,
        "to": TO_NUMBER,
        "url": config.get("TwimlUrl"),
        "machine_detection": config.get("MachineDetection"),
        "async_amd": config.get("AsyncAmd"),
        "async_amd_status_callback_method": config.get("AsyncAmdStatusCallbackMethod"),
        "async_amd_status_callback": config.get("AsyncAmdStatusCallback"),
        "machine_detection_timeout": config.get("MachineDetectionTimeout"),
        "machine_detection_speech_threshold": config.get("MachineDetectionSpeechThreshold"),
        "machine_detection_speech_end_threshold": config.get("MachineDetectionSpeechEndThreshold"),
        "machine_detection_silence_timeout": config.get("MachineDetectionSilenceTimeout"),
    }

def main():
    # Accept num_calls from command line (default 1)
    if len(sys.argv) > 1:
        try:
            num_calls = int(sys.argv[1])
        except Exception:
            print("Invalid argument, using 1 call.")
            num_calls = 1
    else:
        num_calls = 1

    config = load_config(CONFIG_FILE)
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    print(f"\nPlacing {num_calls} calls to {TO_NUMBER} with AMD settings:")
    call_kwargs = build_call_kwargs(config)
    call_kwargs = {k: v for k, v in call_kwargs.items() if v is not None}
    for k, v in call_kwargs.items():
        print(f"  {k}: {v}")

    for i in range(num_calls):
        print(f"\n--- Call {i+1}/{num_calls} ---")
        try:
            call = client.calls.create(**call_kwargs)
            print(f"Call SID: {call.sid} | Status: {call.status}")
        except Exception as e:
            print(f"Error placing call: {e}")
        time.sleep(1)  # avoid rate limiting

if __name__ == "__main__":
    main()
