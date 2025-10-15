from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os

APP_NAME = os.getenv("APP_NAME", "TCG Universe API")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
ENABLE_DEMO_DATA = os.getenv("ENABLE_DEMO_DATA", "true").lower() == "true"

app = FastAPI(title=APP_NAME, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGINS] if ALLOWED_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Product(BaseModel):
    id: int
    name: str
    brand: str  # "Pokemon" | "One Piece"
    category: str  # "singola" | "sigillato" | "lotto" | "accessorio"
    price: float
    image_url: Optional[str] = None
    condition: Optional[str] = "NM"
    set_name: Optional[str] = None

class Listing(BaseModel):
    id: int
    product_id: int
    user_id: int
    title: str
    description: Optional[str] = ""
    price: float
    status: str = "attivo"  # attivo | venduto

class Message(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    receiver_id: int
    text: Optional[str] = None
    offer_value: Optional[float] = None
    trade_items: Optional[list] = None
    image_url: Optional[str] = None

PRODUCTS: List[Product] = []
LISTINGS: List[Listing] = []
MESSAGES: List[Message] = []

if ENABLE_DEMO_DATA:
    PRODUCTS = [
        Product(id=1, name="Charizard EX", brand="Pokemon", category="singola", price=120.0, condition="NM"),
        Product(id=2, name="Booster Box Scarlet & Violet", brand="Pokemon", category="sigillato", price=140.0),
        Product(id=3, name="Monkey D. Luffy Alt Art", brand="One Piece", category="singola", price=95.0, condition="LP"),
    ]
    LISTINGS = [
        Listing(id=1, product_id=1, user_id=100, title="Charizard EX NM", description="Carta in ottime condizioni", price=120.0),
        Listing(id=2, product_id=3, user_id=101, title="Luffy Alt Art", description="Leggera usura", price=95.0),
    ]

@app.get("/health")
def health():
    return {"status": "ok", "app": APP_NAME}

@app.get("/products", response_model=List[Product])
def get_products(brand: Optional[str] = None, q: Optional[str] = None):
    results = PRODUCTS
    if brand:
        results = [p for p in results if p.brand.lower() == brand.lower()]
    if q:
        ql = q.lower()
        results = [p for p in results if ql in p.name.lower() or (p.set_name or "").lower().find(ql) != -1]
    return results

@app.post("/products", response_model=Product)
def create_product(p: Product):
    if any(x.id == p.id for x in PRODUCTS):
        raise HTTPException(status_code=400, detail="ID prodotto già esistente")
    PRODUCTS.append(p)
    return p

@app.get("/listings", response_model=List[Listing])
def get_listings(status: Optional[str] = None):
    if status:
        return [l for l in LISTINGS if l.status == status]
    return LISTINGS

@app.post("/listings", response_model=Listing)
def create_listing(l: Listing):
    if any(x.id == l.id for x in LISTINGS):
        raise HTTPException(status_code=400, detail="ID inserzione già esistente")
    if not any(p.id == l.product_id for p in PRODUCTS):
        raise HTTPException(status_code=404, detail="Prodotto non trovato")
    LISTINGS.append(l)
    return l

@app.patch("/listings/{listing_id}", response_model=Listing)
def update_listing_status(listing_id: int, status: str):
    for l in LISTINGS:
        if l.id == listing_id:
            l.status = status
            return l
    raise HTTPException(status_code=404, detail="Inserzione non trovata")

@app.get("/messages/{chat_id}", response_model=List[Message])
def get_chat(chat_id: int):
    return [m for m in MESSAGES if m.chat_id == chat_id]

@app.post("/messages", response_model=Message)
def send_message(m: Message):
    MESSAGES.append(m)
    return m
