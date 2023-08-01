from TTS.api import TTS
from playsound import playsound

print(TTS.list_models())
model_name = "tts_models/en/vctk/vits"
#p270 - idx 44
# Run TTS

# Init TTS with the target model name
tts = TTS(model_name, progress_bar=True,gpu=False)
#wav = tts.tts("Roses! My favorite!",speaker=tts.speakers[44],emotion="Happy")
# Text to speech to a file
tts.tts_to_file(text="Oh my gosh! Roses are my favorite!", speaker=tts.speakers[44],emotion="Excited", file_path="audio/test.wav")
playsound("audio/test.wav")