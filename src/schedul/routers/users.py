import uuid as uuid_pkg

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select

from clients.sql import get_session
from models.user import User

router = APIRouter(tags=["Users"])


@router.get("/users/{user_uuid}", response_model=User)
def get_user(
    *, session: Session = Depends(get_session), user_uuid: uuid_pkg.UUID
) -> User:
    if user := session.get(User, user_uuid):
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/users", response_model=list[User])
def get_films(
    *,
    session: Session = Depends(get_session),
) -> list[User] | Response:
    return session.exec(select(User)).all() or Response(status_code=204)


@router.post("/users", response_model=User, status_code=201)
def create_user(*, session: Session = Depends(get_session), user: User) -> User:
    db_user = User.from_orm(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.delete("/users/{user_uuid}")
def delete_user(
    *, session: Session = Depends(get_session), user_uuid: uuid_pkg.UUID
) -> dict[str, bool]:
    if user := session.get(User, user_uuid):
        session.delete(user)
        session.commit()
        return {"deleted": True}
    else:
        raise HTTPException(status_code=404, detail="User not found")
