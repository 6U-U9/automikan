from pydantic import BaseModel

class TorrentInfo(BaseModel):
    id: int
    name: str
    download: str
    chosen: bool
    downloading: bool
    finished: bool

from fastapi import APIRouter, Depends, HTTPException, status

from storage.model import User, Torrent
from api.database import get_database
from api.user import get_current_user

router = APIRouter(
    prefix="/torrent",
    tags=["torrent"],
    dependencies=[Depends(get_database)],
    responses={404: {"description": "Not found"}},
)

@router.get("/info/{index}", response_model = TorrentInfo)
def get_torrent_info(index: int, current_user: User = Depends(get_current_user)):
    torrent = Torrent.get_or_none(Torrent.id == index)
    if torrent == None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Torrent not found."
        )
    return torrent


