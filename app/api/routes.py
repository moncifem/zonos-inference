from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database.database import get_db, AudioExampleDB
from ..services.audio_service import AudioService
from .models import AudioExample, AudioGeneration
import os

router = APIRouter()
audio_service = AudioService()

@router.post("/examples/", response_model=AudioExample)
async def create_example(
    description: str,
    language: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    filename = f"example_{hash(file.filename)}.wav"
    audio_service.save_example(file, filename)
    
    db_example = AudioExampleDB(
        description=description,
        filename=filename,
        language=language
    )
    db.add(db_example)
    db.commit()
    db.refresh(db_example)
    return db_example

@router.get("/examples/", response_model=List[AudioExample])
async def get_examples(db: Session = Depends(get_db)):
    return db.query(AudioExampleDB).all()

@router.get("/examples/{example_id}", response_model=AudioExample)
async def get_example(example_id: int, db: Session = Depends(get_db)):
    example = db.query(AudioExampleDB).filter(AudioExampleDB.id == example_id).first()
    if not example:
        raise HTTPException(status_code=404, detail="Example not found")
    return example

@router.delete("/examples/{example_id}")
async def delete_example(example_id: int, db: Session = Depends(get_db)):
    example = db.query(AudioExampleDB).filter(AudioExampleDB.id == example_id).first()
    if not example:
        raise HTTPException(status_code=404, detail="Example not found")
    
    # Delete file
    try:
        os.remove(os.path.join(audio_service.examples_dir, example.filename))
    except:
        pass
    
    db.delete(example)
    db.commit()
    return {"message": "Example deleted"}

@router.post("/generate/")
async def generate_audio(generation: AudioGeneration, db: Session = Depends(get_db)):
    example = db.query(AudioExampleDB).filter(AudioExampleDB.id == generation.example_id).first()
    if not example:
        raise HTTPException(status_code=404, detail="Example not found")
    
    output_path = audio_service.generate_audio(
        generation.text,
        generation.example_id,
        generation.language
    )
    return {"audio_path": output_path} 