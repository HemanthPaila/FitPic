from fastapi import APIRouter, UploadFile, File
from app.services.tryon_service import generate_tryon
from PIL import Image
import io

router = APIRouter()

@router.post("/")
async def tryon(person: UploadFile = File(...), cloth: UploadFile = File(...)):
    person_img = Image.open(io.BytesIO(await person.read())).resize((256,256))
    cloth_img = Image.open(io.BytesIO(await cloth.read())).resize((256,256))

    result = generate_tryon(person_img, cloth_img)

    return {"status": "generated"}
