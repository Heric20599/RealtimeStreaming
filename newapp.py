from flask import Flask, jsonify
import assemblyai as aai
import threading
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Get the AssemblyAI API key from the environment
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

# Set up the transcriber callbacks
def on_open(session_opened: aai.RealtimeSessionOpened):
    print("Session opened with ID:", session_opened.session_id)

def on_data(transcript: aai.RealtimeTranscript):
    if not transcript.text:
        return
    if isinstance(transcript, aai.RealtimeFinalTranscript):
        print("Final transcript:", transcript.text, end="\r\n")
    else:
        print("Partial transcript:", transcript.text, end="\r")

def on_error(error: aai.RealtimeError):
    print("An error occurred:", error)

def on_close():
    print("Closing Session")

# Define the endpoint to start the transcription
@app.route('/start_transcription', methods=['POST'])
def start_transcription():
    transcriber = aai.RealtimeTranscriber(
        sample_rate=16_000,
        on_data=on_data,
        on_error=on_error,
        on_open=on_open,
        on_close=on_close,
    )

    # Connect to the AssemblyAI API
    transcriber.connect()

    # Open a microphone stream
    microphone_stream = aai.extras.MicrophoneStream(sample_rate=16_000)
    
    # Start a new thread for streaming audio
    threading.Thread(target=transcriber.stream, args=(microphone_stream,)).start()
    
    return jsonify({"message": "Transcription started"}), 200

# Define the endpoint to stop the transcription
@app.route('/stop_transcription', methods=['POST'])
def stop_transcription():
    transcriber.close()
    return jsonify({"message": "Transcription stopped"}), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(port=5000, debug=True)
