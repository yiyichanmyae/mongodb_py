from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
from routes import router as book_router

config = dotenv_values(".env")

app = FastAPI()

# from routers.topic_model import tm
# from routers.auth import auth, db_connection
import os
# import nltk
import uvicorn

environment_level = str(os.environ.get("Service_hosting"))
if environment_level == "CloudRun":
    host_name = "0.0.0.0"
else:
    host_name = "localhost"


if __name__ == "__main__":
    uvicorn.run(app, port=int(os.environ.get("PORT", 8000)), host=host_name)

@app.get("/")
async def root():
    return {"message": "Welcome to the PyMongo tutorial!"}

@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    print("Connected to the MongoDB database!")

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

# Register the /book endpoints
app.include_router(book_router, tags=["books"], prefix="/book")

