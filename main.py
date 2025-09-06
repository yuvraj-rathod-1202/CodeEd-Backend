from fastapi import FastAPI
from app.api.v1.routes import router
from app.db.mongodb import connect_to_mongo
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "https://www.elevateed-ai.com",  
    "http://localhost:3000",
    "https://elevateed-ai.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow all origins for development; adjust in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

# @app.on_event("startup")
# async def statup_event():
#     await connect_to_mongo()
#     print("Connected to MongoDB")

app.include_router(router, prefix='/api/v1')

