from pydantic import BaseModel

class EpisodeUpdate(BaseModel):
    id: int
    anime: int | None = None
    index: int | None = None
    special: str | None = None
    title: str | None = None
    alternative_title: str | None = None

class EpisodeOutput(BaseModel):
    id: int
    anime: int
    index: int
    special: str | None = None
    title: str
    alternative_title: str


from fastapi import APIRouter, Depends, HTTPException, status

from storage.model import User, Episode
from api.database import get_database
from api.user import get_current_user

router = APIRouter(
    prefix="/episode",
    tags=["episode"],
    dependencies=[Depends(get_database)],
    responses={404: {"description": "Not found"}},
)

@router.get("/by_anime/{index}", response_model = list[EpisodeOutput])
def get_list_by_anime(index: int, current_user: User = Depends(get_current_user)):
    episodes = Episode.select().where(Episode.anime == index)
    response = []
    for episode in episodes:
        response.append(episode)
    return response

@router.get("/update", response_model = EpisodeOutput)
def update(item: EpisodeUpdate, current_user: User = Depends(get_current_user)):
    episode = Episode.get_or_none(Episode.id == item.id)
    if episode == None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Episode not found."
        )
    for field_name, field in item.model_fields.items():
        if getattr(item, field_name) != None and hasattr(episode, field_name):
            setattr(episode, field_name, getattr(item, field_name))
    episode.save()
    return episode
