from TTS.api import TTS
from playsound import playsound

model_name = "tts_models/en/vctk/vits"
tts = TTS(model_name, progress_bar=True,gpu=False)

def generate_speech(text):
    # Generate the speech
    tts.tts_to_file(text=text, speaker=tts.speakers[41],emotion="Excited", file_path="audio/test.wav")
    playsound("audio/test.wav")

def play_speech(filename):
    # Play the speech
    playsound(filename)
