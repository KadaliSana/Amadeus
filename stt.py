import os
import pyaudio
import wave
import torch
import whisperx

class stt():
    def __init__(self):
        torch.hub.set_dir("D:\\AI\\Amadeus")

        # Setup device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"

        # Load WhisperX model
        model = whisperx.load_model("small", device, compute_type=compute_type)

        # Mic setup
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1024
        RECORD_SECONDS = 5
        DEVICE_INDEX = None

        SAVE_DIR = "D:\\AI\\recordings"
        os.makedirs(SAVE_DIR, exist_ok=True)

        p = pyaudio.PyAudio()
    
    def listen(self):
        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        input_device_index=self.DEVICE_INDEX,
                        frames_per_buffer=self.CHUNK)

        print("🎙️ Listening... Press Ctrl+C to stop.")
        frames = []
        for _ in range(int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = stream.read(self.CHUNK)
            frames.append(data)

        filename = os.path.join(self.SAVE_DIR, f"recording.wav")

        # Save recorded audio
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))

        # Transcribe using WhisperX
        audio = whisperx.load_audio(filename)
        result = self.model.transcribe(audio, batch_size=16)

        os.remove(filename)
        return result["text"]
