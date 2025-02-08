from pydantic import BaseModel
from datetime import date

class AnimeUpdate(BaseModel):
    id: int
    mikan_id: int | None = None
    title: str | None = None
    alternative_title: str | None = None
    season: int | None = None
    air_time: date | None = None
    fliter_rule: str | None = None
    naming_format: str | None = None
    finished: bool | None = None

class AnimeOutput(BaseModel):
    id: int
    mikan_id: int | None = None
    title: str
    alternative_title: str
    season: int
    air_time: date | None = None
    poster_id: int
    fliter_rule: str
    naming_format: str
    finished: bool

from fastapi import APIRouter, Depends, HTTPException, status

from storage.model import User, Anime
from api.database import get_database
from api.user import get_current_user

router = APIRouter(
    prefix="/anime",
    tags=["anime"],
    dependencies=[Depends(get_database)],
    responses={404: {"description": "Not found"}},
)

@router.get("/list", response_model = list[AnimeOutput])
def get_list(offset: int = 0, limit: int | None = None, current_user: User = Depends(get_current_user)):
    animes = Anime.select().offset(offset)
    if limit != None:
        animes = animes.limit(limit)
    response = []
    for anime in animes:
        response.append(anime)
    return response

@router.post("/update", response_model = AnimeOutput)
def update(item: AnimeUpdate, current_user: User = Depends(get_current_user)):
    anime = Anime.get_or_none(Anime.id == item.id)
    if anime == None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Anime not found."
        )
    for field_name, field in item.model_fields.items():
        if getattr(item, field_name) != None and hasattr(anime, field_name):
            setattr(anime, field_name, getattr(item, field_name))
    anime.save()
    return anime

# Todo: delete anime with episode, versions, etc

@router.get("/{index}", response_model = AnimeOutput)
def get_anime(index: int, current_user: User = Depends(get_current_user)):
    anime = Anime.get_or_none(Anime.id == index)
    if anime == None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Anime not found."
        )
    return anime