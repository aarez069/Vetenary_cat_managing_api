import enum
from sqlalchemy import create_engine, Column, Integer, String, Date, Enum
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import date

app = FastAPI()
database_url = "sqlite:///./cats.db"
engine = create_engine(database_url, connect_args={"check_same_thread": False})
localsession = sessionmaker(bind=engine, autoflush=False)
base = declarative_base()


class catstatus(enum.Enum):
    HEALTHY = "healthy"
    SICK = "sick"
    RECOVERING = "recovering"
    ADOPTED = "adopted"


class cat(base):
    __tablename__ = "cats_entries"

    ID = Column(Integer, primary_key=True, index=True)
    Name = Column(String)
    DOB = Column(Date)
    Issue = Column(String)
    Status = Column(Enum(catstatus))


class getcat(BaseModel):
    Name: Annotated[
        str,
        Field(
            ...,
            description="Enter the Cat's name",
        ),
    ]
    DOB: Annotated[date, Field(..., description="Enter date in YYYY-MM-DD format")]
    Issue: Annotated[
        str,
        Field(
            ..., description="Enter the disease or problem the cat is suffering from"
        ),
    ]
    Status: Annotated[
        Literal["HEALTHY", "SICK", "RECOVERING", "ADOPTED"],
        Field(..., description="Choose from HEALTY,SICK,RECOVERING,ADOPTED"),
    ]

    @field_validator("Status", mode="before")
    @classmethod
    def lowercase_status(cls, v: str) -> str:
        return v.upper()


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


@app.post("/add/cat")
def add(new_cat: getcat, db: Session = Depends(pre)):
    new_cat = cat(**new_cat.model_dump())
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return {"message": "The cat has been added to your database", "entry": new_cat}
