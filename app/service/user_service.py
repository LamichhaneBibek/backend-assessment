from random import randint
import secrets
from typing import Optional
from uuid import UUID
import uuid
import re
import logging
from datetime import datetime, timezone

from sqlalchemy.orm.dynamic import AppenderMixin
from app.models import db
from app.models import dto
from app.models import enums
from app.repos import user_repo
from app.core.security import bcrypt_hashing
from app.utils import formatting
from app.mappers import user_mapper
from app.exceptions.scheme import AppException
from app.utils.email import send_verification_email  # Import the function

MIN_PASS = 100000
MAX_PASS = 999999
logger = logging.getLogger(__name__)




def get_all(limit: int = 1000, offset: int = 0) -> list[dto.UserDTO]:
    return [user_mapper.db_to_get_dto(user) for user in user_repo.get(limit, offset)]


def deactivate_user(id: UUID) -> db.UserDB:
    user = user_repo.deactivate_user(id)
    if user is None:
        raise AppException(message="User not found", status_code=404)

    return user

def get_by_id(id: UUID) -> db.UserDB:
    user = user_repo.get_by_id(id)
    if user is None:
        raise AppException(message="User not found", status_code=404)

    return user


def get_by_email(email: str) -> Optional[db.UserDB]:
    if not email:
        return None

    email_formatted = formatting.format_string(email)
    if not _is_valid_email(email_formatted):
        return None

    return user_repo.get_by_email(email_formatted)


def create_user(obj: dto.UserCreateDTO) -> dto.UserDTO:

    email_formatted = formatting.format_string(obj.email)
    if not email_formatted or not _is_valid_email(email_formatted):
        raise AppException(message="Email is not valid", status_code=422)

    name_formatted = formatting.format_string(obj.username)
    if not name_formatted or len(name_formatted) < 2:
        raise AppException(message="Name must be at least 2 characters", status_code=422)

    if not _is_valid_password(obj.password):
        raise AppException(
            message="Password must be at least 8 characters with uppercase, lowercase, number, and special character",
            status_code=422
        )

    existing_user = user_repo.get_by_email(email_formatted)
    if existing_user is not None:
        # Log potential security issue
        logger.warning(f"Registration attempt with existing email: {email_formatted}")
        raise AppException(message="Email already exists", status_code=422)

    try:
        user = _create(obj, enums.UserRole.USER)
        logger.info(f"User created successfully: {user.email}")
        return user_mapper.db_to_get_dto(user)
    except Exception as e:
        logger.error(f"Failed to create user: {str(e)}")
        raise AppException(message=f"Account creation failed. Please try again later.{str(e)}", status_code=500)


def create_admin(obj: dto.UserCreateDTO) -> dto.UserDTO:
    user = _create(obj, enums.UserRole.ADMIN)
    return user_mapper.db_to_get_dto(user)


def _create(obj: dto.UserCreateDTO, role: enums.UserRole) -> db.UserDB:

    try:
        user_to_db = db.UserDB()
        user_to_db.id = uuid.uuid4()
        user_to_db.username = formatting.format_string(obj.username)
        user_to_db.role = role
        user_to_db.email = formatting.format_string(obj.email)
        user_to_db.is_active = True
        user_to_db.hash_password = bcrypt_hashing.hash(obj.password)
        user_to_db.created_at = datetime.now(timezone.utc)

        return user_repo.add(user_to_db)
    except Exception as e:
        logger.error(f"Database error creating user: {str(e)}")
        raise






def _is_valid_email(email: str) -> bool:
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def _is_valid_password(password: str) -> bool:
    """Validate password strength"""
    if len(password) < 8:
        return False

    # Check for at least one uppercase, lowercase, number, and special character
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    return all([has_upper, has_lower, has_digit, has_special])
