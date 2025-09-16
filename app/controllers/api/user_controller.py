from fastapi import APIRouter
from uuid import UUID
from app.models import dto
from app.core import dependencies

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


@router.get("/me", response_model=dto.UserDTO)
def get_me(user: dependencies.user_dependency):
    return user
