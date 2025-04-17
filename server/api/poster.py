from pydantic import BaseModel, HttpUrl
from typing import Optional

class PosterCreate(BaseModel):
    url: HttpUrl

import logging
logger = logging.getLogger(__name__)
import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from manager.global_manager import GlobalManager
from api.user import get_current_user
from api.database import get_database
from storage.model import User, Poster, Anime
from io import BytesIO
from fastapi.responses import StreamingResponse
from PIL import Image

router = APIRouter(
    prefix="/poster",
    tags=["poster"],
    dependencies=[Depends(get_database)],
    responses={404: {"description": "Not found"}},
)

def save_uploaded_file(file: UploadFile) -> str:
    try:
        # Generate the file path and save the file
        file_location = os.path.join(GlobalManager.global_config.poster_directory, file.filename)
        with open(file_location, "wb") as buffer:
            buffer.write(file.file.read())
        logger.debug(f"File saved successfully at {file_location}")
        return file_location
    except Exception as e:
        logger.error(f"Error saving file {file_location}: {str(e)}", stack_debug = True) 

@router.post("/upload")
def upload_poster(anime_id: int = Form(), file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    logger.debug(f"Attempting to upload poster file: {file.filename} for Anime ID: {anime_id}")
    
    anime = Anime.get_or_none(Anime.id == anime_id)
    if not anime:
        logger.error("Anime with ID %d not found.", anime_id)
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Anime not found."
        )
    # Save the file to the server
    file_path = save_uploaded_file(file)
    poster = Poster.create(
        url = "file://" + file_path, 
        path = file.filename, 
        download = True
    )
    poster.save()
    anime.poster = poster
    anime.save()

    logger.debug(f"Poster uploaded and associated with Anime ID: {anime_id} successfully")
    return {"id": poster.id, "url": poster.url, "anime_id": anime_id}

@router.post("/create/{anime_id}")
def create_poster(anime_id: int, data: PosterCreate, current_user: User = Depends(get_current_user)):
    logger.debug("Attempting to set poster URL for Anime ID: %d", anime_id)

    # Check if Anime exists
    anime = Anime.get_or_none(Anime.id == anime_id)
    if not anime:
        logger.error("Anime with ID %d not found.", anime_id)
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Anime not found."
        )

    poster = Poster.create(
        url = data.url, 
        path = None, 
        download = False
    )
    poster.save()
    anime.poster = poster
    anime.save()

    logger.debug("Poster URL set successfully for Anime ID: %d", anime_id)
    return {"anime_id": anime_id, "poster_url": poster.url, "download": poster.download}

@router.get("/delete/{poster_id}")
def delete_poster(poster_id: int, current_user: User = Depends(get_current_user)):
    logger.debug("Attempting to delete poster with ID: %d", poster_id)
    if poster_id == 0:
        logger.warning("Poster with ID %d not found.", poster_id)
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Poster not found."
        )
    
    poster = Poster.get_or_none(Poster.id == poster_id)
    if poster == None:
        logger.error("Poster with ID %d not found.", poster_id)
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Poster not found."
        )
    
    file_path = os.path.join(GlobalManager.global_config.poster_directory, poster.path)
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
        logger.debug("File deleted successfully from server: %s", file_path)

    poster.delete_instance()
    logger.debug("Poster with ID %d deleted successfully.", poster_id)
    return {"id": poster_id}

@router.get("/delete/by_anime/{anime_id}")
def delete_posters_by_anime(anime_id: int, current_user: User = Depends(get_current_user)):
    try:
        logger.debug("Attempting to delete posters for Anime ID: %d", anime_id)

        # Check if Anime exists
        anime = Anime.get_or_none(Anime.id == anime_id)
        if not anime:
            logger.warning("Anime with ID %d not found.", anime_id)
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND, 
                detail="Anime not found."
            )

        if anime.poster:
            poster = anime.poster
            file_path = os.path.join(GlobalManager.global_config.poster_directory, poster.path)
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.debug("File deleted successfully from server: %s", file_path)
            poster.delete_instance()
            anime.poster = 0
            anime.save()
            
            logger.debug("Poster deleted for Anime ID: %d", anime_id)
        else:
            logger.warning("No poster associated with Anime ID %d", anime_id)

        return {"message": "Posters deleted successfully for the Anime."}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Error deleting posters for Anime ID %d: %s", anime_id, str(e))
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error."
        )

@router.get("/get/{poster_id}")
def get_poster(poster_id: int, current_user: User = Depends(get_current_user)):
    poster = Poster.get_or_none(Poster.id == poster_id)
    if poster == None:
        logger.error("Poster with ID %d not found.", poster_id)
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Poster not found."
        )
    
    file_path = os.path.join(GlobalManager.global_config.poster_directory, poster.path)

    if not os.path.exists(file_path):
        logger.error("Poster file not found at path: {file_path}")
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Poster file not found."
        )

    # Open the image and create a binary stream
    with open(file_path, "rb") as f:
        image_content = BytesIO(f.read())
    
    # Check the image format and set the appropriate content type
    image = Image.open(image_content)
    image_format = image.format.lower()  # e.g., 'jpeg', 'png', etc.
    
    # Return the image content as StreamingResponse
    image_content.seek(0)  # Reset stream position before returning
    return StreamingResponse(image_content, media_type = f"image/{image_format}")
    
@router.get("/get/by_anime/{anime_id}")
def get_poster_by_anime(anime_id: int, current_user: User = Depends(get_current_user)):
    logger.debug("Attempting to fetch poster for Anime ID: %d", anime_id)

    anime = Anime.get_or_none(Anime.id == anime_id)
    if not anime:
        logger.warning("Anime with ID %d not found.", anime_id)
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Anime not found."
        )
    
    if not anime.poster:
        logger.warning(f"No poster found for Anime {anime_id}")
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = f"No poster found for Anime {anime_id}"
        )

    file_path = os.path.join(GlobalManager.global_config.poster_directory, anime.poster.path)
    if not os.path.exists(file_path):
        logger.error("Poster file not found at path: {file_path}")
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Poster file not found."
        )

    with open(file_path, "rb") as f:
        image_content = BytesIO(f.read())
    image = Image.open(image_content)
    image_format = image.format.lower()  # e.g., 'jpeg', 'png', etc.
    image_content.seek(0)  
    return StreamingResponse(image_content, media_type = f"image/{image_format}")