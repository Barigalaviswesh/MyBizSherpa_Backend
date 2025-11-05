from pydantic import BaseModel
from typing import List

class TranscriptPayload(BaseModel):
    company: str
    attendees: List[str]
    date: str
    transcript: str
