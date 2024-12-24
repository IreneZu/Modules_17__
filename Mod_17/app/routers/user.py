from fastapi import APIRouter, Depends, status, HTTPException
# Сессия БД
from sqlalchemy.orm import Session
# Функция подключения к БД
from backend.db_depends import get_db
# Аннотации, Модели БД и Pydantic.
from typing import Annotated
from models.user import User
from schemas import CreateUser, UpdateUser
# Функции работы с записями.
from sqlalchemy import insert, select, update, delete
# Функция создания slug-строки
from slugify import slugify

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users


@router.get("/user_id")
async def user_by_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found!')
    return user


@router.post("/create")
async def create_user(db: Annotated[Session, Depends(get_db)]
                          , create_user: CreateUser):
    user_ = db.scalar(select(User).where(User.username == create_user.username))
    if user_  is not None:
    #print(f'create_user.username = {create_user.username}, User.username = {User.username} user_ = {user_}')
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username already exists!')
    db.execute(insert(User).values(
        username=create_user.username,
        firstname = create_user.firstname,
        lastname = create_user.lastname,
        age = create_user.age,
        slug = slugify(create_user.username)))

    db.commit()
    return {'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'}

    db.commit()


@router.put("/update")
async def update_user(db: Annotated[Session, Depends(get_db)], user_id: int
                      , update_user: UpdateUser):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found!')

    db.execute(update(User).where(User.id == user_id).values(
        firstname=update_user.firstname,
        lastname=update_user.lastname,
        age=update_user.age))
    db.commit()

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User update is successful!'
    }


@router.delete("/delete")
async def delete_user(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found!')

    db.execute(delete(User).where(User.id == user_id))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User delete is successful'
    }
