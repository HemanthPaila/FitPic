from fastapi import FastAPI
from app.api.routes import fit, tryon
from fastapi import FastAPI, File, UploadFile
import numpy as np
from services.fit_service import predict_fit
from services.tryon_service import generate_tryon
from PIL import Image
import io

app = FastAPI()

@app.get("/")
def home():
    return {"message": "FitPic API Running"}

@app.post("/predict-fit")
async def fit_endpoint(data: dict):
    result = predict_fit(data["features"])
    return result

@app.post("/tryon")
async def tryon_endpoint(
    person: UploadFile = File(...),
    cloth: UploadFile = File(...)
):
    person_img = Image.open(io.BytesIO(await person.read())).resize((256,256))
    cloth_img = Image.open(io.BytesIO(await cloth.read())).resize((256,256))
    
    result_img = generate_tryon(person_img, cloth_img)

app = FastAPI(title="FitPic API")

app.include_router(fit.router, prefix="/fit", tags=["Fit"])
app.include_router(tryon.router, prefix="/tryon", tags=["TryOn"])

@app.get("/")
def root():
    return {"message": "FitPic API running 🚀"}
