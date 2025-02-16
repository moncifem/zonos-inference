from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from services.audio_service import AudioService
import os
from typing import List

SUPPORTED_LANGUAGES = ["en-us", "ja-jp", "zh-cn", "fr-fr", "de-de"]

app = FastAPI(
    title="Zonos Text-to-Speech API",
    description="""
    A Text-to-Speech API that clones voices from audio samples.
    
    Features:
    - Voice cloning from audio samples
    - Multiple language support
    - High-quality speech synthesis
    """,
    version="1.0.0",
    contact={
        "name": "API Support",
        "url": "https://github.com/Zyphra/Zonos"
    },
)

transformer_service = AudioService(model_type="transformer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/languages", response_model=List[str], tags=["Info"])
async def get_supported_languages():
    """
    Get a list of supported language codes.
    
    Returns:
        List of supported language codes (e.g., ["en-us", "ja-jp", ...])
    """
    return SUPPORTED_LANGUAGES

@app.post("/generate", 
    response_model=dict,
    tags=["Speech"],
    summary="Generate speech from text",
    response_description="Generated audio data in WAV format"
)
async def generate_speech(
    text: str = Form(..., description="The text to convert to speech", example="Hello, this is a test"),
    speaker_file: UploadFile = File(..., description="A 10-30 second WAV file of the voice to clone"),
    language: str = Form(default="en-us", description="Language code for the text")
):
    """
    Generate speech from text using voice cloning.

    Parameters:
    - **text**: The text you want to convert to speech
    - **speaker_file**: A WAV audio file (10-30 seconds) of the voice you want to clone
    - **language**: Language code (e.g., en-us, ja-jp, zh-cn, fr-fr, de-de)

    Returns:
    - **success**: Boolean indicating if generation was successful
    - **audio**: Binary audio data (WAV format) if successful
    - **error**: Error message if unsuccessful
    """
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported language. Must be one of: {', '.join(SUPPORTED_LANGUAGES)}"
        )

    if not speaker_file.filename.endswith('.wav'):
        raise HTTPException(
            status_code=400,
            detail="Speaker file must be a WAV file"
        )

    temp_path = f"temp_speaker_{hash(speaker_file.filename)}.wav"
    try:
        with open(temp_path, "wb") as f:
            f.write(await speaker_file.read())

        output_path = transformer_service.generate_speech(text, temp_path, language)
        with open(output_path, "rb") as f:
            audio_data = f.read()

        return JSONResponse(
            content={"success": True, "audio": audio_data},
            headers={"Content-Disposition": f"attachment; filename=generated_speech.wav"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if 'output_path' in locals() and os.path.exists(output_path):
            os.remove(output_path)

@app.get("/", tags=["Info"])
async def root():
    """
    Get API information and status.
    """
    return {
        "status": "online",
        "service": "Zonos TTS API",
        "endpoints": [
            {"path": "/generate", "method": "POST", "description": "Generate speech from text"},
            {"path": "/languages", "method": "GET", "description": "List supported languages"}
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1) 