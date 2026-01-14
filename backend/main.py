import os
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import user, product, order, category, cart

app = FastAPI(
    title="E-Commerce API",
    version="1.0 | BETA"
    )

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