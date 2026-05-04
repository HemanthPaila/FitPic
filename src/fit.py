from fastapi import APIRouter
from app.schemas.fit_schema import FitRequest
from app.services.fit_service import predict_fit

router = APIRouter()

@router.post("/")
def fit_prediction(request: FitRequest):
    return predict_fit(request.features)
