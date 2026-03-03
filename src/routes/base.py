from fastapi import FastAPI, APIRouter, Depends
from helpers import get_settings, Settings

base_router = APIRouter(
    prefix='/api/v1',
    tags=["api_v1"]
)

@base_router.get("/")
async def health_check(settings : Settings = Depends(get_settings)):
  return {
    "Welcome To My Application ": settings.APP_NAME
  }