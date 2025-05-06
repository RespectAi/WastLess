# app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .db import engine, SessionLocal, Base
from . import schemas, crud, models
from typing import List
from .schemas import FridgeUserCreate, FridgeUserRead, NotificationRead
from .schemas import (
    FridgeItemCreate,
    FridgeItemRead,
    FridgeItemUpdate
)
# 1) Create all tables in the database (no-ops if they already exist)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="WasteLess API")

# 2) Dependency: get a database session, ensure it closes after use
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 3) A simple “ping” endpoint
@app.get("/ping")
def ping():
    return {"message": "WasteLess is up!"}

# 4) READ: List all users
@app.get("/users/", response_model=list[schemas.UserRead])
def list_users(db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return users

# 5) CREATE: a new user
@app.post(
    "/users/",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED
)
def create_user_endpoint(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    # ensure email isn’t already taken
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return crud.create_user(db, user)

# 6) UPDATE an existing user
@app.put(
    "/users/{user_id}",
    response_model=schemas.UserRead
)
def update_user_endpoint(
    user_id: int,
    user_in: schemas.UserBase,
    db: Session = Depends(get_db)
):
    updated = crud.update_user(db, user_id, user_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated

# 7) DELETE a user
@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db)
):
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

# --- FRIDGE ROUTES ---

@app.get("/fridges/", response_model=list[schemas.FridgeRead])
def list_fridges(db: Session = Depends(get_db)):
    return crud.get_fridges(db)

@app.post("/fridges/", response_model=schemas.FridgeRead, status_code=status.HTTP_201_CREATED)
def create_fridge_endpoint(fridge: schemas.FridgeCreate, db: Session = Depends(get_db)):
    return crud.create_fridge(db, fridge)

@app.put("/fridges/{fridge_id}", response_model=schemas.FridgeRead)
def update_fridge_endpoint(
    fridge_id: int,
    fridge_in: schemas.FridgeBase,
    db: Session = Depends(get_db)
):
    updated = crud.update_fridge(db, fridge_id, fridge_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fridge not found"
        )
    return updated

@app.delete("/fridges/{fridge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fridge_endpoint(fridge_id: int, db: Session = Depends(get_db)):
    success = crud.delete_fridge(db, fridge_id)
    if not success:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Fridge not found")
    return

# 8) LIST people sharing a fridge
@app.get(
    "/fridges/{fridge_id}/users/",
    response_model=List[FridgeUserRead]
)
def list_fridge_users_endpoint(
    fridge_id: int,
    db: Session = Depends(get_db)
):
    return crud.list_fridge_users(db, fridge_id)


# 9) SHARE: add a user to a fridge
@app.post(
    "/fridges/{fridge_id}/users/",
    response_model=FridgeUserRead,
    status_code=status.HTTP_201_CREATED
)
def add_user_to_fridge_endpoint(
    fridge_id: int,
    share: FridgeUserCreate,
    db: Session = Depends(get_db)
):
    # Optionally: verify fridge exists
    if not crud.get_fridge(db, fridge_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Fridge not found")
    # Optionally: verify user exists
    if not crud.get_user(db, share.user_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    return crud.add_user_to_fridge(db, fridge_id, share)


# 10) REVOKE: remove a user’s access
@app.delete(
    "/fridges/{fridge_id}/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_user_from_fridge_endpoint(
    fridge_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    success = crud.remove_user_from_fridge(db, fridge_id, user_id)
    if not success:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Fridge-User mapping not found"
        )

# 11) LIST items in a fridge
@app.get(
    "/fridges/{fridge_id}/items/",
    response_model=List[schemas.FridgeItemRead]
)
def list_fridge_items_endpoint(
    fridge_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_fridge_items(db, fridge_id, skip, limit)


# 12) CREATE a new item
@app.post(
    "/fridges/{fridge_id}/items/",
    response_model=schemas.FridgeItemRead,
    status_code=status.HTTP_201_CREATED
)
def create_fridge_item_endpoint(
    fridge_id: int,
    item: FridgeItemCreate,
    db: Session = Depends(get_db)
):
    # Verify fridge exists
    if not crud.get_fridge(db, fridge_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Fridge not found")

    return crud.create_fridge_item(db, fridge_id, item)


# 13) UPDATE an item
@app.put(
    "/items/{item_id}",
    response_model=schemas.FridgeItemRead
)
def update_fridge_item_endpoint(
    item_id: int,
    item_in: FridgeItemUpdate,
    db: Session = Depends(get_db)
):
    updated = crud.update_fridge_item(db, item_id, item_in)
    if not updated:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Item not found")
    return updated


# 14) DELETE an item
@app.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_fridge_item_endpoint(
    item_id: int,
    db: Session = Depends(get_db)
):
    success = crud.delete_fridge_item(db, item_id)
    if not success:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Item not found")
    return

# 15) LIST a user’s notifications
@app.get(
    "/users/{user_id}/notifications/",
    response_model=List[schemas.NotificationRead]
)
def list_notifications_endpoint(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_notifications_for_user(db, user_id, skip, limit)


# 16) MARK a notification as sent
@app.post(
    "/notifications/{note_id}/send",
    status_code=status.HTTP_204_NO_CONTENT
)
def send_notification_endpoint(
    note_id: int,
    db: Session = Depends(get_db)
):
    success = crud.mark_notification_sent(db, note_id)
    if not success:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Notification not found")


# 17) GENERATE notifications on demand
@app.post(
    "/notifications/generate",
    response_model=List[schemas.NotificationRead]
)
def generate_notifications_endpoint(db: Session = Depends(get_db)):
    new_notes = crud.generate_notifications(db)
    return new_notes
