import librosa
from pathlib import Path
import sounddevice as sd
import wavio

def record(duration=5, fs=48000):
    sd.default.samplerate = fs
    sd.default.channels = 1
    myrecording = sd.rec(int(duration * fs))
    sd.wait(duration)
    return myrecording

def save_record(path_myrecording, myrecording, fs):
    wavio.write(path_myrecording, myrecording, fs, sampwidth=2)
    return None
