import os
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import user, product, order, category, cart
from backend.core.cache import close_redis
from backend.core.rabbitmq import close_rabbitmq

from backend.core.exception_handlers import register_exception_handlers

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        await close_redis()
        await close_rabbitmq()

app = FastAPI(
    title="E-Commerce API",
    version="1.0 | BETA",
    lifespan=lifespan
    )

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("static"):
    os.makedirs("static/products")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user.router, prefix="/api")
app.include_router(product.router, prefix="/api")
app.include_router(order.router, prefix="/api")
app.include_router(category.router, prefix="/api")
app.include_router(cart.router, prefix="/api")
app.include_router(product.admin_router, prefix="/api")
app.include_router(order.admin_router, prefix="/api")
app.include_router(category.admin_router, prefix="/api")
