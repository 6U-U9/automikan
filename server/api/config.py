import logging
logger = logging.getLogger(__name__)

from typing import Any
from pydantic import BaseModel
from datetime import timedelta
from config.config import Pattern

class ConfigBaseModel(BaseModel):
    # Logging
    logging_path: str | None
    logging_level: int | None
    return_detail_error_info: bool | None
    enable_api_doc: bool | None

    # User (Not implemented yet)
    single_user: bool | None

    # API
    host: str | None
    port: int | None
    CORS_origins: list[str] | None

    # Torrent
    torrent_directory: str | None
    save_all_torrent: bool | None
    delete_unreferenced_torrent: bool | None

    # Mikan
    mikan_bangumi_rss_template: str | None

    # Download
    bangumi_directory: str | None
    poster_directory: str | None
    global_naming_format: str | None
    select_by_episode: bool | None
    remove_covered_download: bool | None
    background_job_interval: int | None
    version_check_timeout: timedelta | None

    # Downloader
    downloader: str | None
    downloader_connection_info: dict[str, Any] | None
    
    # Network
    proxy: str | None = None
    request_header: dict[str, str] | None
    
    # Database
    database_url: str | None
    database_pragmas: dict[str, Any] | None

    # Pattern
    add_name_parse_result_to_common: bool | None
    # special for title
    name_parse_pattern_fields: list[str] | None
    name_parse_patterns: dict[str, Pattern] | None

    pattern_title_exclude_front: list[str] | None 
    pattern_title_exclude_back: list[str] | None
    pattern_title_exclude_char: str | None
    
    # Fliter
    default_fliter_rule: dict[str, Any] | None

class ConfigUpdate(ConfigBaseModel):
    pass

class ConfigOutput(ConfigBaseModel):
    pass

from fastapi import APIRouter, Depends, HTTPException, status

from manager.global_manager import GlobalManager
from storage.model import User
from api.user import get_current_user

router = APIRouter(
    prefix="/config",
    tags=["config"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model = ConfigOutput)
def get_config(current_user: User = Depends(get_current_user)):
    return GlobalManager.global_config

@router.post("/", response_model = ConfigOutput)
def update_config(item: ConfigUpdate, current_user: User = Depends(get_current_user)):
    global_config = GlobalManager.global_config
    for field_name, field in item.model_fields.items():
        if getattr(item, field_name) != None and hasattr(global_config, field_name):
            setattr(global_config, field_name, getattr(item, field_name))
    GlobalManager.save_config(GlobalManager.config_path)
    return global_config
