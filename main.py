from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi import FastAPI, HTTPException, Depends

app = FastAPI()
database_url = "sqlite:///./cats.db"
engine = create_engine(database_url, connect_args={"check_same_thread": False})
localsession = sessionmaker(bind=engine, autoflush=False)
base = declarative_base()


class cat(base):
    __tablename__ = "cats_entries"

    ID = Column(Integer, primary_key=True, index=True)
    Name = Column(String)
    DOB = Column(Date)
    Issue = Column(String)


base.metadata.create_all(bind=engine)


def pre():
    db = localsession()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home(db: Session = Depends(pre)):
    return {"message": "This is a veternary cat manager"}
