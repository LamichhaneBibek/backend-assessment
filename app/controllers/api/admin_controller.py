from fastapi import APIRouter
from fastapi import Query
from uuid import UUID
from app.models import dto
from app.core import dependencies
from app.service import user_service

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/users", response_model=list[dto.UserDTO])
def get_all_users(user: dependencies.admin_dependency, limit: int = Query(1000, gt=0), offset: int = Query(0, ge=0)):
    print(f"user {user}")
    return user_service.get_all(limit, offset)

@router.get("/logs", response_model=dto.UserDTO)
def get_logs(user: dependencies.admin_dependency):
    return user

@router.post("/users/{id}/deactivate", response_model=dto.UserDTO)
def deactivate_user(user: dependencies.admin_dependency,id: UUID):
    print(f"user {user}")
    return user_service.deactivate_user(id)
