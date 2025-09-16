from uuid import UUID
from app.models.db import UserDB
import logging
from app.exceptions.scheme import AppException
from app.core.db_context import session_maker
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

logger = logging.getLogger(__name__)


def add(user: UserDB) -> UserDB:
    try:
        with session_maker.begin() as session:
            session.add(user)
            session.flush()  # Flush to get any constraint violations
            return user
    except IntegrityError as e:
        logger.error(f"Database integrity error: {str(e)}")
        if "email" in str(e):
            raise AppException(message="Email already exists", status_code=422)
        else:
            raise AppException(message="Database constraint violation", status_code=422)
    except SQLAlchemyError as e:
        logger.error(f"Database error in add_user: {str(e)}")
        raise AppException(message="Database error occurred", status_code=500)

def get_by_id(id: UUID) -> UserDB | None:
    with session_maker() as session:
        return session.query(UserDB).where(
            UserDB.id == id
        ).first()



def get(limit:int = 1000, offset: int = 0) -> list[UserDB]:
    with session_maker() as session:
        return session.query(UserDB).limit(limit).offset(offset).all()

def deactivate_user(id: UUID) -> UserDB | None:
    with session_maker() as session:
        user = session.query(UserDB).where(UserDB.id == id).first()
        if not user:
            return None
        user.is_active = False
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def get_by_email(email: str) -> UserDB:
    """Get user by email"""
    try:
        with session_maker() as session:
            return session.query(UserDB).filter(
                UserDB.email == email
            ).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_by_email: {str(e)}")
        raise AppException(message="Database error occurred", status_code=500)
