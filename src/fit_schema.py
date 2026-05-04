from pydantic import BaseModel
from typing import List

class FitRequest(BaseModel):
    features: List[float]
