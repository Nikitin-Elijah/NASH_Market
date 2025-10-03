from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import users, products


app = FastAPI(description='NASH market API', version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(products.router)


@app.get('/')
async def root() -> dict:
    return {'message': 'NASH market API root'}