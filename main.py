from fastapi import FastAPI
from app.api.v1.routes import router
from app.services.firebase.config import FirebaseConfig
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://elevate-ed-phi.vercel.app/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow all origins for development; adjust in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin", "Access-Control-Allow-Origin"],
)

@app.on_event("startup")
async def statup_event():
    firebase_config = FirebaseConfig()
    firebase_config.initialize_firebase()
    print("Connected to Firebase")
    

app.include_router(router, prefix='/api/v1')

