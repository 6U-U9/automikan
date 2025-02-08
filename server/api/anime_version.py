from pydantic import BaseModel

class AnimeVersionUpdate(BaseModel):
    id: int
    anime: int | None = None
    provider_id: int | None = None
    format: str | None = None
    audio_coding: str | None = None
    video_coding: str | None = None
    resolution: str | None = None
    source: str | None = None
    subtitle: str | None = None

class AnimeVersionOutput(BaseModel):
    id: int
    anime: int
    provider_id: int
    format: str
    audio_coding: str
    video_coding: str
    resolution: str
    source: str
    subtitle: str


from fastapi import APIRouter, Depends, HTTPException, status

from storage.model import User, AnimeVersion
from api.database import get_database
from api.user import get_current_user

router = APIRouter(
    prefix="/anime_version",
    tags=["anime_version"],
    dependencies=[Depends(get_database)],
    responses={404: {"description": "Not found"}},
)

@router.get("/by_anime/{index}", response_model = list[AnimeVersionOutput])
def get_list_by_anime(index: int, current_user: User = Depends(get_current_user)):
    anime_versions = AnimeVersion.select().where(AnimeVersion.anime == index)
    response = []
    for anime_version in anime_versions:
        response.append(anime_version)
    return response

@router.post("/update", response_model = AnimeVersionOutput)
def update(item: AnimeVersionUpdate, current_user: User = Depends(get_current_user)):
    anime_version = AnimeVersion.get_or_none(AnimeVersion.id == item.id)
    if anime_version == None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Anime version not found."
        )
    for field_name, field in item.model_fields.items():
        if getattr(item, field_name) != None and hasattr(anime_version, field_name):
            setattr(anime_version, field_name, getattr(item, field_name))
    anime_version.save()
    return anime_version
