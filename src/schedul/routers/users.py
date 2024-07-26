import uuid as uuid_pkg

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session

from schedul.clients.sql import get_session
from schedul.models.user import User
from schedul.services.users import (
    create_user_db,
    delete_user_db,
    get_user_db,
    get_users_db,
)

router = APIRouter(tags=["Users"])


@router.get("/users/{user_uuid}", response_model=User)
def get_user(
    *, session: Session = Depends(get_session), user_uuid: uuid_pkg.UUID
) -> User:
    if user := get_user_db(session=session, user_uuid=user_uuid):
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/users", response_model=list[User])
def get_users(
    *,
    session: Session = Depends(get_session),
) -> list[User] | Response:
    return get_users_db(session=session) or Response(status_code=204)


@router.post("/users", response_model=User, status_code=201)
def create_user(*, session: Session = Depends(get_session), user: User) -> User:
    return create_user_db(session=session, user=user)


@router.delete("/users/{user_uuid}")
def delete_user(
    *, session: Session = Depends(get_session), user_uuid: uuid_pkg.UUID
) -> dict[str, bool]:
    if delete_user_db(session=session, user_uuid=user_uuid):
        return {"deleted": True}
    else:
        raise HTTPException(status_code=404, detail="User not found")
