from fastapi import FastAPI, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import engine, SessionLocal
from pydantic import BaseModel

class PaymentAmount(BaseModel):
    payment_amount: float

class Points(BaseModel):
    points: int

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/wallet/{user_id}", response_model=schemas.WalletOut)
def get_wallet(user_id: int, db: Session = Depends(get_db)):
    return crud.get_wallet(db, user_id)


@app.post("/api/wallet/{user_id}/add", response_model=schemas.WalletOut)
def add_points(user_id: int, payment: PaymentAmount = Body(...), db: Session = Depends(get_db)):
    return crud.add_points(db, user_id, payment.payment_amount)


@app.post("/api/wallet/{user_id}/use", response_model=schemas.RedeemResponse)
def use_points(user_id: int, points_data: Points = Body(...), db: Session = Depends(get_db)):
    return crud.redeem_points(db, user_id, points_data.points)


@app.post("/api/wallet/{user_id}/redeem", response_model=schemas.RedeemResponse)
def redeem_points(user_id: int, points_data: Points = Body(...), db: Session = Depends(get_db)):
    return crud.redeem_points(db, user_id, points_data.points)


@app.post("/api/wallet/{user_id}/voucher", response_model=schemas.VoucherResponse)
def voucher(user_id: int, points_data: Points = Body(...), db: Session = Depends(get_db)):
    return crud.exchange_for_voucher(db, user_id, points_data.points)
