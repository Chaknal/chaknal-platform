from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.database import async_session_maker
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from app.models.duxsoup_user import DuxSoupUser

router = APIRouter(prefix="/api/duxsoup-users", tags=["duxsoup-users"])


class DuxSoupUserCreate(BaseModel):
    dux_soup_user_id: str
    dux_soup_auth_key: str
    email: EmailStr
    first_name: str
    last_name: str


class DuxSoupUserResponse(BaseModel):
    id: str
    dux_soup_user_id: str
    dux_soup_auth_key: str
    email: str
    first_name: str
    last_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class DuxSoupUserUpdate(BaseModel):
    dux_soup_user_id: Optional[str] = None
    dux_soup_auth_key: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


async def get_db():
    async with async_session_maker() as session:
        yield session


@router.post("/", response_model=List[DuxSoupUserResponse])
async def create_duxsoup_users(
    users: List[DuxSoupUserCreate],
    db: AsyncSession = Depends(get_db)
):
    created = []
    for user_data in users:
        dux_user = DuxSoupUser(
            dux_soup_user_id=user_data.dux_soup_user_id,
            dux_soup_auth_key=user_data.dux_soup_auth_key,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )
        db.add(dux_user)
        created.append(dux_user)
    await db.commit()
    
    # Refresh all created users to get their IDs and timestamps
    for user in created:
        await db.refresh(user)
    
    return created


@router.post("/single", response_model=DuxSoupUserResponse)
async def create_duxsoup_user(
    user: DuxSoupUserCreate,
    db: AsyncSession = Depends(get_db)
):
    dux_user = DuxSoupUser(
        dux_soup_user_id=user.dux_soup_user_id,
        dux_soup_auth_key=user.dux_soup_auth_key,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    db.add(dux_user)
    await db.commit()
    await db.refresh(dux_user)
    return dux_user


@router.get("/", response_model=List[DuxSoupUserResponse])
async def get_all_duxsoup_users(db: AsyncSession = Depends(get_db)):
    """Get all DuxSoup users"""
    result = await db.execute(select(DuxSoupUser))
    users = result.scalars().all()
    return users


@router.get("/{user_id}", response_model=DuxSoupUserResponse)
async def get_duxsoup_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific DuxSoup user by ID"""
    result = await db.execute(select(DuxSoupUser).where(DuxSoupUser.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=DuxSoupUserResponse)
async def update_duxsoup_user(
    user_id: str, 
    user_update: DuxSoupUserUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Update a DuxSoup user"""
    result = await db.execute(select(DuxSoupUser).where(DuxSoupUser.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update only provided fields
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_duxsoup_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a DuxSoup user"""
    result = await db.execute(select(DuxSoupUser).where(DuxSoupUser.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully"}
