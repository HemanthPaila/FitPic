from fastapi import FastAPI
from app.api.routes import fit, tryon

app = FastAPI(title="FitPic API")

app.include_router(fit.router, prefix="/fit", tags=["Fit"])
app.include_router(tryon.router, prefix="/tryon", tags=["TryOn"])

@app.get("/")
def root():
    return {"message": "FitPic API running 🚀"}
