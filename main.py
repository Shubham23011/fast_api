from fastapi import FastAPI,Depends,HTTPException
from mangum import Mangum
from pydantic import BaseModel
from typing import Annotated,List
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
handler = Mangum(app)

origins = [
    'http://localhost:3000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


class TransactionBase(BaseModel):
    amount : float
    category : str
    description : str
    is_income : bool
    date : str

class TransactionModel(TransactionBase):
    id : int

    class Config:
        orm_mode = True



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

models.Base.metadata.create_all(bind=engine)

@app.post("/transactions/",response_model=TransactionModel)
async def create_transaction(transaction : TransactionBase, db: db_dependency):
    db_transaction = models.Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@app.get("/transactions/",response_model=List[TransactionModel])
async def read_transaction(db: db_dependency, skip : int=0, limit: int=100):
    transactions = db.query(models.Transaction).offset(skip).limit(limit).all()
    return transactions