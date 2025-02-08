from pydantic import BaseModel

class EpisodeVersionOutput(BaseModel):
    id: int
    episode_id: int
    anime_version_id: int
    torrnet_id: str

from fastapi import APIRouter, Depends, HTTPException, status

from storage.model import User, EpisodeVersion
from api.database import get_database
from api.user import get_current_user

router = APIRouter(
    prefix="/episode_version",
    tags=["episode_version"],
    dependencies=[Depends(get_database)],
    responses={404: {"description": "Not found"}},
)

@router.get("/by_episode/{index}", response_model = list[EpisodeVersionOutput])
def get_list_by_episode(index: int, current_user: User = Depends(get_current_user)):
    episode_versions = EpisodeVersion.select().where(EpisodeVersion.episode == index)
    response = []
    for episode_version in episode_versions:
        response.append(episode_version)
    return response

@router.get("/by_anime_version/{index}", response_model = list[EpisodeVersionOutput])
def get_list_by_anime_version(index: int, current_user: User = Depends(get_current_user)):
    episode_versions = EpisodeVersion.select().where(EpisodeVersion.version == index)
    response = []
    for episode_version in episode_versions:
        response.append(episode_version)
    return response


