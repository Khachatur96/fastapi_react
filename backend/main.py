from typing import List

from fastapi import FastAPI, security, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

import schemas
import services
from schemas import UserCreate
from sqlalchemy import orm

from services import get_db, get_user_by_email, create_user_obj, authenticate_user, create_token, get_current_user

app = FastAPI()


@app.post("/api/users")
async def create_user(user: UserCreate, db: orm.Session = Depends(get_db)):
    db_user = await get_user_by_email(user.email, db)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    user = await create_user_obj(user, db)

    return await create_token(user)


@app.post("/api/token")
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends(), db: orm.Session = Depends(get_db)):
    user = await authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")
    return await create_token(user)


@app.get("/api/users/me", response_model=schemas.User)
async def get_user(user: schemas.User = Depends(get_current_user)):
    return user


@app.post("/api/leads", response_model=schemas.Lead)
async def create_lead(lead: schemas.LeadCreate, user: schemas.User = Depends(get_current_user),
                      db: orm.Session = Depends(get_db)):
    return await services.create_lead(user=user, db=db, lead=lead)


@app.get("/api/leads", response_model=List[schemas.Lead])
async def get_leads(user: schemas.User = Depends(get_current_user),
                    db: orm.Session = Depends(get_db)):
    return await services.get_leads(user=user, db=db)


@app.get("/api/leads/{lead_id}", status_code=200)
async def get_lead_by_id(lead_id: int, user: schemas.User = Depends(get_current_user),
                         db: orm.Session = Depends(get_db)):
    return await services._lead_selector(lead_id=lead_id, user=user, db=db)


@app.delete("/api/leads/{lead_id}", status_code=204)
async def delete_lead(
        lead_id: int,
        user: schemas.User = Depends(services.get_current_user),
        db: orm.Session = Depends(services.get_db),
):
    await services.delete_lead(lead_id, user, db)
    return {"message", "Successfully Deleted"}


@app.put("/api/leads/{lead_id}", status_code=200)
async def update_lead(
        lead_id: int,
        lead: schemas.LeadCreate,
        user: schemas.User = Depends(services.get_current_user),
        db: orm.Session = Depends(services.get_db),
):
    await services.update_lead(lead_id, lead, user, db)
    return {"message", "Successfully Updated"}


@app.get("/api")
async def root():
    return {"message": "Awesome Lead's Manager"}
