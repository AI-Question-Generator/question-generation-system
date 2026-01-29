from fastapi import FastAPI, APIRouter, Depends
from helpers import get_setting, Settings

base_router = APIRouter(
  prefix="/base",
  tags=["base"]
)

@base_router.get("/")
async def health_check(settings : Settings = Depends(get_setting)):
  # settings = get_setting()
  return {
    "Welcome To My Application ": settings.APP_NAME
  }