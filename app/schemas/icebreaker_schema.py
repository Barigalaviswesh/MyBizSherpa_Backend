from pydantic import BaseModel
from typing import Optional

class Icebreaker(BaseModel):
    name:str
    linkedin_bio:str
    pitch_deck_text:Optional[str] = None
    

