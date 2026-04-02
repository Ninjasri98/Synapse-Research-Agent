from pydantic import BaseModel, Field
from typing import List

class AudioOverviewSingleTranscript(BaseModel):
    name: str = Field(..., description="The name of the person speaking")
    transcript: str = Field(..., description="The transcript of the person speaking")

class AudioOverviewTranscript(BaseModel):
    transcript: List[AudioOverviewSingleTranscript] = Field(..., description="The transcript of the audio overview")