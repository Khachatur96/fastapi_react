import os
from datetime import datetime
from typing import List

import jwt
from fastapi import security, Depends, HTTPException
from sqlalchemy import orm
from passlib.hash import bcrypt

import models
import schemas
from database import SessionLocal, Base, engine
from models import User
from schemas import UserCreate

oauth2schema = security.OAuth2PasswordBearer(tokenUrl="/api/token")
JWT_SECRET = os.urandom(24)


def create_database():
    return Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_user_by_email(email: str, db: orm.Session):
    return db.query(User).filter(User.email == email).first()


async def create_user_obj(user: UserCreate, db: orm.Session):
    user = User(email=user.email, hashed_password=bcrypt.hash(user.hashed_password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def authenticate_user(email: str, password: str, db: orm.Session):
    user = await get_user_by_email(email, db)
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user


async def create_token(user: User):
    user_obj = schemas.User.from_orm(user)

    token = jwt.encode(user_obj.dict(), JWT_SECRET)

    return dict(access_token=token, token_type="bearer")


async def get_current_user(db: orm.Session = Depends(get_db), token: str = Depends(oauth2schema)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        print(payload)
        user = db.query(User).get(payload["id"])
    except Exception as e:
        raise HTTPException(status_code=401, detail="User does not exists")

    return schemas.User.from_orm(user)


async def create_lead(user: schemas.User, db: orm.Session, lead: schemas.LeadCreate):
    lead = models.Lead(**lead.dict(), owner_id=user.id)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return schemas.Lead.from_orm(lead)


async def get_leads(user: schemas.User, db: orm.Session):
    leads = db.query(models.Lead).filter_by(owner_id=user.id)
    return list(map(schemas.Lead.from_orm, leads))


async def _lead_selector(lead_id: int, user: schemas.User, db: orm.Session):
    lead = (
        db.query(models.Lead)
        .filter_by(owner_id=user.id)
        .filter(models.Lead.id == lead_id)
        .first()
    )

    if lead is None:
        raise HTTPException(status_code=404, detail="Lead does not exist")

    return lead


async def delete_lead(lead_id: int, user: schemas.User, db: orm.Session):
    lead = await _lead_selector(lead_id, user, db)

    db.delete(lead)
    db.commit()


async def update_lead(lead_id: int, lead: schemas.LeadCreate, user: schemas.User, db: orm.Session):
    lead_db = await _lead_selector(lead_id, user, db)

    lead_db.first_name = lead.first_name
    lead_db.last_name = lead.last_name
    lead_db.email = lead.email
    lead_db.company = lead.company
    lead_db.note = lead.note
    lead_db.date_last_updated = datetime.utcnow()

    db.commit()
    db.refresh(lead_db)

    return schemas.Lead.from_orm(lead_db)
