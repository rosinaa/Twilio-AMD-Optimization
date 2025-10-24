from flask import Flask, request, Response, send_file
from twilio.twiml.voice_response import VoiceResponse
import os, threading, subprocess, csv, time
from urllib.parse import unquote, urlparse, parse_qs
from colorama import init, Fore, Style
import argparse

init(autoreset=True)
app = Flask(__name__)

AUDIO_CSV = "recording_urls.csv"
audio_urls = []
with open(AUDIO_CSV, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        audio_urls.append(row["Audio"])
        # audio_urls.pop(0)

with open("current_audio_url.txt", "w") as f:
    f.write(audio_urls[0])

pending_audio_urls = audio_urls.copy()   # Queue of remaining audio files to test
call_audio_assignment = {}               # call_sid -> audio_url mapping
completed_calls = set()
audio_queue_lock = threading.Lock()

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)
CALL_RESULTS_CSV = os.path.join(REPORTS_DIR, "call_results.csv")
print(f"pending_audio_urls: {pending_audio_urls}")
print(f"call_audio_assignment start: {call_audio_assignment}")

# Write CSV header if file does not exist
if not os.path.exists(CALL_RESULTS_CSV):
    with open(CALL_RESULTS_CSV, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "timestamp", "call_sid", "audio_url", "event_sequence",
            "call_status", "answered_by", "callback_source"
        ])

def log_call_event(timestamp, call_sid, audio_url, sequence=None, call_status=None, answered_by=None, callback_source=None):
    with open(CALL_RESULTS_CSV, "a", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            timestamp,
            call_sid,
            audio_url,
            sequence,
            call_status,
            answered_by,
            callback_source
        ])

def place_next_call():
    with audio_queue_lock:
        if not pending_audio_urls:
            print(Fore.GREEN + "[INFO] All test calls have been placed and processed." + Style.RESET_ALL)
            return
        # Pop next audio URL for testing
        next_audio_url = pending_audio_urls.pop(0)
        # Store in shared file for next call
        with open("current_audio_url.txt", "w") as f:
            f.write(next_audio_url)
        print(Fore.BLUE + f"[INFO] Placing call for audio: {next_audio_url}" + Style.RESET_ALL)
        subprocess.Popen([
            "python3", "automated_amd_call.py"
        ])

@app.route("/incoming-call", methods=["GET", "POST"])
def incoming_call():
    call_sid = request.values.get("CallSid", "")

    # Map the call_sid to its audio on first request (if not already)
    with audio_queue_lock:
        if call_sid not in call_audio_assignment:
            # Use the most recently assigned audio file
            try:
                with open("current_audio_url.txt") as f:
                    audio_url = f.read().strip()
                call_audio_assignment[call_sid] = audio_url
            except Exception:
                audio_url = ""
        else:
            audio_url = call_audio_assignment[call_sid]

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{audio_url}</Play>
</Response>
"""
    print(f"[INCOMING CALL] CallSid: {call_sid} -> {audio_url}")

    timestamp = request.values.get("Timestamp", time.strftime('%Y-%m-%d %H:%M:%S'))
    query = urlparse(audio_url).query
    params = parse_qs(query)
    recording_sid = params.get("recording", [None])[0]  
    log_call_event(
        timestamp=timestamp,
        call_sid=call_sid,
        audio_url=recording_sid,
        callback_source="inbound"
    )


    return Response(twiml, mimetype="text/xml")

def parse_webhook_data(request_obj):
    data = {}
    form_data = request_obj.form if request_obj.method == 'POST' else request_obj.args
    for key, value in form_data.items():
        data[key] = unquote(str(value))
    return data

def color_status(status):
    if status == "initiated":   return Fore.BLUE + status + Style.RESET_ALL
    if status == "ringing":     return Fore.YELLOW + status + Style.RESET_ALL
    if status == "in-progress": return Fore.CYAN + status + Style.RESET_ALL
    if status == "completed":   return Fore.GREEN + status + Style.RESET_ALL
    if status == "busy":        return Fore.MAGENTA + status + Style.RESET_ALL
    return status

def color_amd(answered_by):
    if not answered_by: return ""
    val = answered_by.lower()
    if val == "human": return Fore.GREEN + Style.BRIGHT + "HUMAN"
    if "machine" in val: return Fore.MAGENTA + Style.BRIGHT + answered_by.upper()
    if "fax" in val: return Fore.YELLOW + Style.BRIGHT + answered_by.upper()
    if val == "unknown": return Fore.RED + Style.BRIGHT + "UNKNOWN"
    return Fore.WHITE + Style.BRIGHT + answered_by.upper()

@app.route("/webhook", methods=['GET', 'POST'])
def handle_webhook():
    parsed_data = parse_webhook_data(request)
    callback_source = parsed_data.get("CallbackSource") or parsed_data.get("CallbackSource".lower())
    call_sid = parsed_data.get("CallSid")
    call_status = parsed_data.get("CallStatus")
    sequence = parsed_data.get("SequenceNumber")
    answered_by = parsed_data.get("AnsweredBy")
    timestamp = parsed_data.get("Timestamp", time.strftime('%Y-%m-%d %H:%M:%S'))

    # Find the audio URL that was served for this call, or empty string if not found
    audio_url = call_audio_assignment.get(call_sid, "")
    # Log the event (always, for all progress events)
    log_call_event(
        timestamp=timestamp,
        call_sid=call_sid,
        audio_url=audio_url,
        sequence=sequence,
        call_status=call_status,
        answered_by=answered_by,
        callback_source=callback_source
    )

    if answered_by:
            print(f"  >>>  AnsweredBy: {color_amd(answered_by)}")

    if callback_source == "call-progress-events":
        print(
            f"{Style.DIM}[{timestamp}]{Style.RESET_ALL} "
            f"{Fore.WHITE}[SID:{call_sid}] [Seq:{sequence}] {Style.RESET_ALL}"
            f"Status: {color_status(call_status)}", end=""
        )
        if call_status == "completed" and call_sid not in completed_calls:
            completed_calls.add(call_sid)
            # Only launch next call if there are more to place
            place_next_call()

    return str(VoiceResponse())

@app.route('/audio.wav', methods=['GET', 'POST'])
def get_audio():
    recording_sid = request.args.get("recording", type=str)
    # Path to the audio file
    audio_path = f"{audio_dir}/{recording_sid}.wav"

    # send_file automatically sets correct headers
    return send_file(audio_path, mimetype="audio/wav")
    # use mimetype="audio/wav" for .wav files, etc.

if __name__ == "__main__":
    print("Minimal Twilio AMD Server running (serving TwiML <Play> for /incoming-call)")
    parser = argparse.ArgumentParser(description="Batch analyzer with parameters")
    parser.add_argument("--audio_dir", required=False, default="channel_audio/left", help="Name of input folder with the recordings to analyze")
    args = parser.parse_args()
    audio_dir = args.audio_dir
    app.run(host='0.0.0.0', port=5000, debug=False)
