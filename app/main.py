from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.services.audio_service import AudioService
import os

app = FastAPI(title="Zonos TTS API")

# Initialize both models
transformer_service = AudioService(model_type="transformer")
hybrid_service = AudioService(model_type="hybrid")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate/")
async def generate_speech(
    text: str = Form(...),
    speaker_file: UploadFile = File(...),
    language: str = Form(default="en-us"),
    model_type: str = Form(default="transformer")
):
    """
    Generate speech from text using a speaker reference
    - text: Text to convert to speech
    - speaker_file: 10-30s audio file for voice cloning
    - language: Supported languages: en-us, ja-jp, zh-cn, fr-fr, de-de
    - model_type: Either "transformer" or "hybrid"
    """
    if model_type not in ["transformer", "hybrid"]:
        return {"success": False, "error": "Invalid model type"}
    
    service = transformer_service if model_type == "transformer" else hybrid_service
    
    # Save the uploaded speaker file
    temp_path = f"temp_speaker_{hash(speaker_file.filename)}.wav"
    with open(temp_path, "wb") as f:
        f.write(await speaker_file.read())

    try:
        # Generate speech
        output_path = service.generate_speech(text, temp_path, language)
        
        # Read the generated file
        with open(output_path, "rb") as f:
            audio_data = f.read()

        # Clean up
        os.remove(temp_path)
        os.remove(output_path)

        return {
            "success": True,
            "audio": audio_data
        }
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1) 