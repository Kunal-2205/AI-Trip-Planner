from typing import List, Optional
from pydantic import BaseModel


class TransportOption(BaseModel):
    mode: str
    available: bool
    estimated_price: int
    duration: str
    distance_km: float
    pros: List[str]
    cons: List[str]


class TransportResponse(BaseModel):
    source: str
    destination: str

    # Instead of string, store the complete transport option
    recommended_mode: Optional[TransportOption] = None

    options: List[TransportOption]