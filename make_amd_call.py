import os
import json
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
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

def main():
    config = load_config(CONFIG_FILE)
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    # Build parameter dictionary for call creation
    call_kwargs = {
        "from_": FROM_NUMBER,
        "to": TO_NUMBER,
        "url": config.get("TwimlUrl"),

        # AMD settings
        "machine_detection": config.get("MachineDetection"),
        "async_amd": config.get("AsyncAmd"),
        "async_amd_status_callback_method": config.get("AsyncAmdStatusCallbackMethod"),
        "async_amd_status_callback": config.get("AsyncAmdStatusCallback"),
        "machine_detection_timeout": config.get("MachineDetectionTimeout"),
        "machine_detection_speech_threshold": config.get("MachineDetectionSpeechThreshold"),
        "machine_detection_speech_end_threshold": config.get("MachineDetectionSpeechEndThreshold"),
        "machine_detection_silence_timeout": config.get("MachineDetectionSilenceTimeout"),

        # Status callback for answered_by and call events
        "status_callback": config.get("StatusCallback"),
        "status_callback_method": config.get("StatusCallbackMethod", "POST"),
        "status_callback_event": config.get("StatusCallbackEvent", ["initiated", "ringing", "answered", "completed"])
    }

    # Remove None values (for optional parameters)
    call_kwargs = {k: v for k, v in call_kwargs.items() if v is not None}

    print("Placing call with AMD and Status Callback settings:")
    for k, v in call_kwargs.items():
        print(f"  {k}: {v}")

    try:
        call = client.calls.create(**call_kwargs)
        print("\nCall placed!")
        print(f"Call SID: {call.sid}")
        print(f"Status: {call.status}")
        print(f"To: {TO_NUMBER}")
        print(f"From: {FROM_NUMBER}")
    except Exception as e:
        print("Error placing call:", e)

if __name__ == "__main__":
    main()
