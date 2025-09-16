from app.models import db
from app.models import dto


def db_to_get_dto(user_db: db.UserDB) -> dto.UserDTO:
    """Convert a User DB object to a GetUser DTO"""
    return dto.UserDTO(
        id=user_db.id,
        username=user_db.username,
        role=user_db.role,
        email=user_db.email,
        is_active= user_db.is_active,
        updated_at=user_db.updated_at,
        created_at=user_db.created_at
    )
