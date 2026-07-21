import enum
from sqlalchemy import create_engine, Column, Integer, String, Date, Enum
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi import FastAPI, HTTPException, Depends, Query
from typing import Annotated, Literal, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import date

app = FastAPI()
database_url = "sqlite:///./cats.db"
engine = create_engine(database_url, connect_args={"check_same_thread": False})
localsession = sessionmaker(bind=engine, autoflush=False)
base = declarative_base()


class catstatus(enum.StrEnum):
    HEALTHY = "healthy"
    SICK = "sick"
    RECOVERING = "recovering"
    ADOPTED = "adopted"


class catgender(enum.StrEnum):
    MALE = "male"
    FEMALE = "female"


class cat(base):
    __tablename__ = "cats_entries"

    ID = Column(Integer, primary_key=True, index=True)
    Name = Column(String)
    DOB = Column(Date)
    Issue = Column(String)
    Status = Column(Enum(catstatus))
    Gender = Column(Enum(catgender))


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
    Gender: Annotated[
        Literal["MALE", "FEMALE"], Field(..., description="Choose from Male or Female")
    ]

    @field_validator("Status", mode="before")
    @classmethod
    def uppercase_status(cls, v: str) -> str:
        return v.upper()

    @field_validator("Gender", mode="before")
    @classmethod
    def gender_status(cls, v: str) -> str:
        return v.upper()


class fetchcat(BaseModel):
    Name: Annotated[
        Optional[str],
        Field(description="Enter the Cat's name", default=None),
    ]
    DOB: Annotated[
        Optional[date],
        Field(description="Enter date in YYYY-MM-DD format", default=None),
    ]
    Issue: Annotated[
        Optional[str],
        Field(
            description="Enter the disease or problem the cat is suffering from",
            default=None,
        ),
    ]
    Status: Annotated[
        Optional[Literal["HEALTHY", "SICK", "RECOVERING", "ADOPTED"]],
        Field(description="Choose from HEALTY,SICK,RECOVERING,ADOPTED", default=None),
    ]
    Gender: Annotated[
        Optional[Literal["MALE", "FEMALE"]],
        Field(description="Choose from Male or Female", default=None),
    ]

    @field_validator("Status", mode="before")
    @classmethod
    def lowercase_status(cls, v: str) -> str:
        if v is None:
            return None
        return v.upper()

    @field_validator("Gender", mode="before")
    @classmethod
    def gender_status(cls, v: str) -> str:
        if not v:
            return None
        return v.upper()


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


@app.get("/view")
def view_data(db: Session = Depends(pre)):
    data = db.query(cat).all()
    if not data:
        raise HTTPException(status_code=404, detail="No entries yet!!!")
    return data


@app.get("/view/specific")
def view_specific(
    cat_specific: fetchcat = Query(
        description="Enter the required fields you wish to search"
    ),
    db: Session = Depends(pre),
):
    query = db.query(cat)
    to_search = cat_specific.model_dump(exclude_unset=True)
    for key, value in to_search.items():
        if value is not None:
            query = query.filter(getattr(cat, key) == value)
    data = query.all()
    if not data:
        raise HTTPException(status_code=404, detail="No such entry found !!!")
    return {"message": "The cats that match your criterion are these:", "Cats": data}


@app.put("/update/{cat_id}")
def update_cat(cat_id: int, cat_updated_details: fetchcat, db: Session = Depends(pre)):
    new_details = cat_updated_details.model_dump(exclude_unset=True)
    subject = db.query(cat).filter(cat.ID == cat_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="No such entry found !!!")
    for key, value in new_details.items():
        setattr(subject, key, value)
    db.commit()
    data = db.query(cat).filter(cat.ID == cat_id).all()
    return {
        "message": "The provided data has been updated successfully!!!",
        "Updated Entry": data,
    }


@app.delete("/delete/{cat_id}")
def delete_cat(cat_id: int, db: Session = Depends(pre)):
    cat_subject = db.query(cat).filter(cat.ID == cat_id).first()
    if not cat_subject:
        raise HTTPException(status_code=404, detail="No such entry found!!!")
    db.delete(cat_subject)
    db.commit()
    return {"message": "The entry has been deleted!!!"}
