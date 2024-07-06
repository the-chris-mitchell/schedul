import uuid as uuid_pkg

from sqlmodel import Session, select

from models.user import User


def create_user_db(session: Session, user: User) -> User:
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def delete_user_db(session: Session, user_uuid: uuid_pkg.UUID) -> bool:
    if user := session.get(User, user_uuid):
        session.delete(user)
        session.commit()
        return True
    return False


def create_user_if_required_db(session: Session, user: User) -> User:
    query = session.exec(select(User).where(User.uuid == user.uuid)).first()
    return query or create_user_db(session=session, user=user)


def get_user_db(session: Session, user_uuid: uuid_pkg.UUID) -> User | None:
    return session.get(User, user_uuid)


def get_users_db(session: Session):
    return list(session.exec(select(User)).all())
