from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()

from app.routers.app_routes import app_routes  


app = FastAPI()

app.include_router(app_routes)

@app.get("/")
def root():
    return{"message" : "Agente proyecJ"}