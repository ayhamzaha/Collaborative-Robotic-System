import os
import wave
import pyaudio
import json
import threading
from vosk import Model, KaldiRecognizer

MODEL_PATH = "src/model"

# Check if the model folder exists
if not os.path.exists(MODEL_PATH):
    print(f"Model folder not found at: {MODEL_PATH}")
    exit(1)
model = Model(MODEL_PATH)

# Flag to control when to stop recording
recording = True

def wait_for_enter():
    global recording
    input("Press ENTER to stop recording...\n")
    recording = False

def record_audio(filename="audio.wav", rate=16000, chunk=1024):
    """ Records audio from the microphone until Enter is pressed """
    global recording
    recording = True  # Reset flag

    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, frames_per_buffer=chunk)

    frames = []
    print("Recording... Press ENTER to stop.")

    # Start a thread to wait for Enter key
    input_thread = threading.Thread(target=wait_for_enter)
    input_thread.start()

    while recording:
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    print("Recording finished.")

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b"".join(frames))

def transcribe_audio(filename="audio.wav"):
    """ Transcribes audio using Vosk """
    with wave.open(filename, "rb") as wf:
        recognizer = KaldiRecognizer(model, wf.getframerate())
        recognizer.SetWords(True)

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            recognizer.AcceptWaveform(data)

        result = json.loads(recognizer.FinalResult())
        words = [word["word"] for word in result.get("result", [])]
        return words
