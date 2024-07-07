from sqlmodel import Session, select

from models.screening import Screening, ScreeningCreate


def create_screening_db(session: Session, screening: ScreeningCreate) -> Screening:
    db_screening = Screening.model_validate(screening)
    session.add(db_screening)
    session.commit()
    session.refresh(db_screening)
    return db_screening


def create_screening_if_required_db(
    session: Session, screening: ScreeningCreate
) -> Screening:
    query = session.exec(
        select(Screening)
        .where(Screening.film_id == screening.film_id)
        .where(Screening.festival_id == screening.festival_id)
        .where(Screening.venue_id == screening.venue_id)
        .where(Screening.start_time_utc == screening.start_time_utc)
    ).first()
    return query or create_screening_db(session=session, screening=screening)


def get_screening_db(session: Session, screening_id: int) -> Screening | None:
    return session.get(Screening, screening_id)


def get_screenings_db(session: Session) -> list[Screening]:
    return list(session.exec(select(Screening)).all())


def delete_screening_db(session: Session, screening_id: int):
    if screening := session.get(Screening, screening_id):
        session.delete(screening)
        session.commit()
        return True
    return False


def get_festival_screenings_db(session: Session, festival_id) -> list[Screening]:
    return list(
        session.exec(
            select(Screening).where(Screening.festival_id == festival_id)
        ).all()
    )
