from sqlalchemy import DateTime, Enum, Integer, String, Boolean, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.functions import current_time, current_timestamp

from app.models import enums

Base = declarative_base()


class UserDB(Base):
    __tablename__ = "users"

    id = mapped_column("id", UUID, primary_key=True)
    username = mapped_column("username", String)
    email = mapped_column("email", String, unique=True)
    hash_password = mapped_column("hash_password", String)
    role = mapped_column("role", Enum(enums.UserRole), default=enums.UserRole.USER)
    is_active = mapped_column("is_active", Boolean, default=False, nullable=False)
    updated_at = mapped_column(
        "updated_at",
        DateTime(),
        server_default=current_timestamp(),
        server_onupdate=current_time(),
    )
    created_at = mapped_column(
        "created_at", DateTime(), server_default=current_timestamp()
    )

class TaskLog(Base):
    __tablename__ = "task_logs"

    id = mapped_column("id", UUID(as_uuid=True), primary_key=True)
    task_id = mapped_column("task_id", String, unique=True, index=True, nullable=False)
    task_name = mapped_column("task_name", String, nullable=False)
    status = mapped_column("status", String, nullable=False)  # pending, success, failure, retry
    result = mapped_column("result", String, nullable=True)
    error_message = mapped_column("error_message", String, nullable=True)

    updated_at = mapped_column(
        "updated_at",
        DateTime(),
        server_default=current_timestamp(),
        server_onupdate=current_time(),
    )
    created_at = mapped_column(
        "created_at", DateTime(), server_default=current_timestamp()
    )
