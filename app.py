from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dist.counter2.counter2 import router as counter2

app = FastAPI()

app.include_router(counter2)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
