from fastapi import FastAPI
import uvicorn

from config import Config
from api.routes import router

app = FastAPI(
    title=Config.APP_NAME,
    description=Config.DESCRIPTION,
    version=Config.VERSION
)
app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True
    )
