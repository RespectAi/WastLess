# app/crud.py

from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from . import models, schemas
from .schemas import FridgeCreate, FridgeBase, FridgeItemCreate, FridgeItemUpdate, NotificationCreate
from typing import List, Literal, Optional


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email,
        password_hash=user.password_hash,
        name=user.name,
        created_at=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserBase):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    if user_update.email is not None:
        db_user.email = user_update.email
    if user_update.name is not None:
        db_user.name = user_update.name
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True

def get_fridge(db: Session, fridge_id: int):
    return db.query(models.Fridge).filter(models.Fridge.fridge_id == fridge_id).first()

def get_fridges(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Fridge).offset(skip).limit(limit).all()

def create_fridge(db: Session, fridge: schemas.FridgeCreate):
    db_fridge = models.Fridge(
        name=fridge.name,
        location_desc=fridge.location_desc,
        created_at=datetime.utcnow()
    )
    db.add(db_fridge)
    db.commit()
    db.refresh(db_fridge)
    return db_fridge

def update_fridge(db: Session, fridge_id: int, fridge_in: schemas.FridgeBase):
    db_fridge = get_fridge(db, fridge_id)
    if not db_fridge:
        return None
    db_fridge.name = fridge_in.name
    db_fridge.location_desc = fridge_in.location_desc
    db.commit()
    db.refresh(db_fridge)
    return db_fridge

def delete_fridge(db: Session, fridge_id: int):
    db_fridge = get_fridge(db, fridge_id)
    if not db_fridge:
        return False
    db.delete(db_fridge)
    db.commit()
    return True

def add_user_to_fridge(
    db: Session,
    fridge_id: int,
    share: schemas.FridgeUserCreate
) -> models.FridgeUser:
    """Share a fridge with a user."""
    # Optional: check fridge and user exist
    mapping = models.FridgeUser(
        fridge_id=fridge_id,
        user_id=share.user_id,
        role=share.role
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping

def remove_user_from_fridge(
    db: Session,
    fridge_id: int,
    user_id: int
) -> bool:
    """Revoke a user’s access to a fridge."""
    mapping = db.query(models.FridgeUser).get((fridge_id, user_id))
    if not mapping:
        return False
    db.delete(mapping)
    db.commit()
    return True

def list_fridge_users(
    db: Session,
    fridge_id: int
) -> List[models.FridgeUser]:
    return db.query(models.FridgeUser).filter_by(fridge_id=fridge_id).all()

def get_fridge_item(db: Session, item_id: int):
    return db.query(models.FridgeItem).filter(models.FridgeItem.item_id == item_id).first()

def get_fridge_items(db: Session, fridge_id: int, skip: int = 0, limit: int = 100) -> List[models.FridgeItem]:
    return (
        db.query(models.FridgeItem)
          .filter(models.FridgeItem.fridge_id == fridge_id)
          .offset(skip)
          .limit(limit)
          .all()
    )

def create_fridge_item(db: Session, fridge_id: int, item: FridgeItemCreate):
    # Compute spoil_date
    if item.opened_at:
        spoil = item.opened_at + timedelta(days=item.open_life_days)
    else:
        spoil = item.factory_expires_at

    db_item = models.FridgeItem(
        fridge_id=fridge_id,
        added_by=item.added_by,
        qr_code=item.qr_code,
        added_at=datetime.utcnow(),
        factory_expires_at=item.factory_expires_at,
        opened_at=item.opened_at,
        open_life_days=item.open_life_days,
        spoil_date=spoil
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_fridge_item(db: Session, item_id: int, item_in: FridgeItemUpdate):
    db_item = get_fridge_item(db, item_id)
    if not db_item:
        return None
    if item_in.opened_at is not None:
        db_item.opened_at = item_in.opened_at
    if item_in.open_life_days is not None:
        db_item.open_life_days = item_in.open_life_days
    # re-compute spoil_date
    if db_item.opened_at:
        db_item.spoil_date = db_item.opened_at + timedelta(days=db_item.open_life_days)
    else:
        db_item.spoil_date = db_item.factory_expires_at
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_fridge_item(db: Session, item_id: int) -> bool:
    db_item = get_fridge_item(db, item_id)
    if not db_item:
        return False
    db.delete(db_item)
    db.commit()
    return True

def get_notifications_for_user(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.Notification]:
    return (
        db.query(models.Notification)
          .filter(models.Notification.user_id == user_id)
          .offset(skip)
          .limit(limit)
          .all()
    )

def mark_notification_sent(db: Session, note_id: int) -> bool:
    note = db.query(models.Notification).get(note_id)
    if not note:
        return False
    note.sent = True
    db.commit()
    return True

def create_notification(db: Session, notif: NotificationCreate):
    db_note = models.Notification(
        item_id=notif.item_id,
        user_id=notif.user_id,
        type=notif.type,
        notified_at=datetime.utcnow(),
        sent=notif.sent
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def generate_notifications(db: Session):
    """
    Scan fridge_items for spoil_date <= today+1 (about_to_spoil)
    or <= today (spoiled), then insert any missing notifications.
    """
    today = date.today()
    upcoming = today + timedelta(days=1)

    # Fetch all relevant items with their fridge users
    rows = (
      db.query(models.FridgeItem, models.FridgeUser)
        .join(models.FridgeUser, models.FridgeItem.fridge_id == models.FridgeUser.fridge_id)
        .filter(models.FridgeItem.spoil_date <= upcoming)
        .all()
    )

    created = []
    for item, share in rows:
        # Decide type
        typ = 'spoiled' if item.spoil_date <= today else 'about_to_spoil'
        # Skip if already exists un-sent
        exists = db.query(models.Notification).filter_by(
            item_id=item.item_id,
            user_id=share.user_id,
            type=typ,
            sent=False
        ).first()
        if exists:
            continue
        notif = NotificationCreate(
            item_id=item.item_id,
            user_id=share.user_id,
            type=typ
        )
        created.append(create_notification(db, notif))
    return created
