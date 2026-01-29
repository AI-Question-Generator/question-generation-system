from fastapi import FastAPI
from routes import base_router, data_router
from helpers import get_setting, Settings
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
  
  settings = get_setting()

  app.mongodb_conn = AsyncIOMotorClient(settings.MONGODB_URL)
  app.db_client = app.mongodb_conn[settings.MONGODB_DATABASE]

@app.on_event("shutdown")
async def shutdown_db_client():
  app.mongodb_conn.close()

app.include_router(base_router)
app.include_router(data_router)

