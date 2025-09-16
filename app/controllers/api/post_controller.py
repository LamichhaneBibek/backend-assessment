from fastapi import APIRouter
from fastapi import Query
from uuid import UUID
from app.models import dto
from app.core import dependencies
from app.service import user_service, post_service

router = APIRouter(
    prefix="/posts",
    tags=["Post"]
)


@router.get("", response_model=dto.UserDTO)
def get_all_posts(limit: int = Query(1000, gt=0), offset: int = Query(0, ge=0)):
    return post_service

@router.get("/{id}", response_model=list[dto.UserDTO])
def get_post_by_id():
    return user_service.get_all(limit, offset)
