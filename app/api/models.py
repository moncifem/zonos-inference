from pydantic import BaseModel
from typing import Optional

class AudioExample(BaseModel):
    id: Optional[int] = None
    description: str
    filename: str
    language: str

class AudioGeneration(BaseModel):
    text: str
    example_id: int
    language: str = "en-us" 