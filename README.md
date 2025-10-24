# Twilio AMD Audio Analysis Toolkit and Automated AMD Tests

This repository contains tools to analyze Twilio Answering Machine Detection (AMD) performance using `.wav` recordings from real calls. It includes utilities for audio channel separation, event correlation, AMD parameter tuning, and visual inspection of detection behavior.

---

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/fvmach/Twilio-AMD-Optimization-Engine.git
cd Twilio-AMD-Optimization-Engine
```

### 2. Install Dependencies

Create a virtual environment (optional):

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Install required packages:

```bash
pip install -r requirements.txt
```

If a `requirements.txt` is not available, install the dependencies manually:

```bash
pip install pydub numpy scipy matplotlib
```

**Note:** `ffmpeg` must be installed and available in your system's PATH for audio processing with `pydub`.

---

## Script Usage

### `split_audio_channels.py`

This script scans the recordings folder for all `.wav` files, identifies stereo audio, splits each into separate mono channel files.

**Usage:**

```bash
python split_audio_channels.py
```

**Output:**

* Input: Stereo `.wav` files
* Output: `channel_audio/left` and `channel_audio/right` folders containing `filename_left.wav` and `filename_right.wav`

---

### `channel_visualization.py` 

This script analyzes `.wav` recordings in the `channel_audio/left` in conjunction with AMD event data (JSON or logs) to produce annotated visualizations.

**Usage:**

```bash
python channel_visualization.py
```

If you want to change the input folder to analyse, use the `input_dir` parameter:

```bash
python channel_visualization.py --input_dir channel_audio/right
```

**Output:**

* PNG waveform visualizations with markers for speech segments, silence, and AMD detection points. The images are stored in the `channel_analysis` folder.

## Run Automated AMD Tests

### Set up Calla and AMD configuration

Update the call and AMD configuration in the `amd_config.json` file. You have to update the following parameters:
* StatusCallback: "https://{{your_domain}}.ngrok.app/webhook"
* AsyncAmdStatusCallback: "https://{{your_domain}}.ngrok.app/webhook",

### `recording_urls.csv`
Add the list of calls and recordings you want to analyze in each batch. The file has to follow the following format: `Call_sid,https://{{your_domain}}.ngrok.app/audio.wav?recording=Recording_file_name_left`

You have to add the file name of the channel you want to analyze. If your callee is in the left channel, then you add the name of the left_channel recording:

https://{{your_domain}}.ngrok.app/audio.wav?recording={{Recording_file_name_left}}

## Example `recording_urls.csv` Contents

CALL_SID,Audio
CA123abc456ef,https://your_domain.ngrok.app/audio.wav?recording=RE5559963asdf
CAxxxxxx,https://your_domain.ngrok.app/audio.wav?recording=REaaabbbccc


### Running the Flask Server

This file runs the Flask server with the AMD and Status Callback webhooks:

```bash
python server.py
```

If you want to change the isolated channel recording to analyze the right channel, use the `audio_dir` parameter:

```bash
python server.py --audio_dir channel_audio/right
```

### Run your Ngrok server

```bash
ngrok http 5000
```

Then, use the forwarding URL provided by ngrok in your Twilio webhook configuration.


### Execute the AMD automated tests

To run all the automated AMD calls executing the `automated_amd_call.py` script.

**Usage:**

```bash
python automated_amd_call.py
```


---

## AMD Parameter Tuning

Twilio AMD allows tuning its detection engine using four parameters:

| Parameter                            | Valid Range   | Default |
| ------------------------------------ | ------------- | ------- |
| `MachineDetectionTimeout`            | 3–59 seconds  | 30      |
| `MachineDetectionSpeechThreshold`    | 1000–6000 ms  | 2400    |
| `MachineDetectionSpeechEndThreshold` | 500–5000 ms   | 1200    |
| `MachineDetectionSilenceTimeout`     | 2000–10000 ms | 5000    |

These parameters influence how the AMD engine reacts to detected speech and silence. Adjusting them helps optimize detection accuracy across different voicemail and greeting styles.

**Official documentation:**
[Twilio AMD Optional Parameters](https://www.twilio.com/docs/voice/answering-machine-detection#optional-parameters)

---

## Tools and Analysis Capabilities

This toolkit provides:

* Stereo channel isolation for separate inspection of input and output audio
* Speech and silence segmentation
* Annotated waveform visualization with AMD detection markers
* Parameter impact evaluation across real-world recordings
* Identification of race conditions or detection anomalies
* AMD call automation

---

## Folder Structure (after processing)

```
.
├── channel_audio/left/        # Mono channel files (left)
├── channel_audio/right/       # Mono channel files (right)
├── channel_analysis/          # Annotated waveform plots
├── recordings/*.wav           # Original recordings
├── reports/                   # CSV log of all the webhooks received
├── *.json / *.log             # Optional metadata or AMD event logs
├── split_audio_channels.py
├── channel_visualization.py
├── server.py
├── automated_amd_call.py
└── README.md
```

---

## Best Practices for Fine-Tuning

* Use a diverse set of recordings with varying environments and greeting types
* Tune parameters incrementally for precision
* Prefer `AsyncAmd` in production use cases
* Visually validate detection behavior before deploying changes

---

## License

MIT License
© Fernando Vieira Machado
