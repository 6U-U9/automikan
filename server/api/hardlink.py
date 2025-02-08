from pydantic import BaseModel

class HardLinkOutput(BaseModel):
    id: int
    link_file_path: str
    origin_file_path: str

from fastapi import APIRouter, Depends

from storage.model import User, HardLink
from api.database import get_database
from api.user import get_current_user

router = APIRouter(
    prefix="/hardlink",
    tags=["hardlink"],
    dependencies=[Depends(get_database)],
    responses={404: {"description": "Not found"}},
)

@router.get("/by_episode_version/{index}", response_model = list[HardLinkOutput])
def get_list_by_episode_version(index: int, current_user: User = Depends(get_current_user)):
    hardlinks = HardLink.select().where(HardLink.episode == index)
    response = []
    for hardlink in hardlinks:
        response.append(hardlink)
    return response