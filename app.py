from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import torch
import torchaudio
import io
import base64
from zonos.model import Zonos
from zonos.conditioning import make_cond_dict
from zonos.utils import DEFAULT_DEVICE as device

app = FastAPI(title="Zonos TTS API")

# Initialize model globally
model = Zonos.from_pretrained("Zyphra/Zonos-v0.1-transformer", device=device)

class TTSRequest(BaseModel):
    text: str
    language: str = "en-us"

@app.post("/tts")
async def text_to_speech(
    request: TTSRequest,
    speaker_audio: UploadFile = File(...)
) -> dict:
    """
    Convert text to speech using provided speaker audio sample
    """
    # Read and process speaker audio
    audio_data = await speaker_audio.read()
    audio_stream = io.BytesIO(audio_data)
    wav, sampling_rate = torchaudio.load(audio_stream)
    
    # Generate speaker embedding
    speaker = model.make_speaker_embedding(wav, sampling_rate)
    
    # Prepare conditioning and generate audio
    cond_dict = make_cond_dict(
        text=request.text,
        speaker=speaker,
        language=request.language
    )
    conditioning = model.prepare_conditioning(cond_dict)
    codes = model.generate(conditioning)
    
    # Convert to audio and encode as base64
    wavs = model.autoencoder.decode(codes).cpu()
    buffer = io.BytesIO()
    torchaudio.save(buffer, wavs[0], model.autoencoder.sampling_rate, format="wav")
    audio_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return {"audio": audio_base64} 