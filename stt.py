import os
import pyaudio
import wave
import torch
import nemo.collections.asr as nemo_asr
import soundfile as sf

class STT:
    def __init__(self):
        # Load Parakeet model
        self.model = nemo_asr.models.EncDecCTCModel.from_pretrained(
            model_name="nvidia/parakeet-tdt-0.6b-v2"
        )

        # Audio settings
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000  # NeMo expects 16kHz
        self.CHUNK = 1024
        self.RECORD_SECONDS = 5
        self.DEVICE_INDEX = None

        # Save path
        self.SAVE_DIR = "recordings"
        os.makedirs(self.SAVE_DIR, exist_ok=True)

        self.p = pyaudio.PyAudio()

    def listen(self):
        stream = self.p.open(format=self.FORMAT,
                             channels=self.CHANNELS,
                             rate=self.RATE,
                             input=True,
                             input_device_index=self.DEVICE_INDEX,
                             frames_per_buffer=self.CHUNK)

        print("🎙️ Listening for 5 seconds...")

        frames = []
        for _ in range(int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = stream.read(self.CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()

        filename = os.path.join(self.SAVE_DIR, "recording.wav")
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        # Optionally resave using soundfile for correct format
        data, sr = sf.read(filename)
        sf.write(filename, data, sr, subtype='PCM_16')

        # Transcribe with Parakeet
        result = self.model.transcribe([filename])[0].text

        os.remove(filename)
        return result
