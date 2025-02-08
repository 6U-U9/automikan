import logging
logger = logging.getLogger(__name__)
import os
import argparse

import asyncio
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from config.config import Config
from storage.storage import Storage, db_state_default
from storage.model import User, Anime, Provider
from utils.string import concat_re_pattern

class GlobalManager():
    config_path: str
    global_config: Config
    # 1. title to mikan_id:     "title"             ->  dict[str : int]
    # 2. provider to mikan_id:  "provider"          ->  dict[str : int]
    # 3. common_pattern:        "common_pattern"    ->  dict[str : str]
    global_cache: dict = dict(
        title = {},
        provider = {},
        common_pattern = {},
    )
    storage: Storage
    scheduler: AsyncIOScheduler
    job: Job
    managers: list = []
    app: FastAPI

    def __init__(self):
        raise NotImplementedError("This class cannot be instantiated")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        GlobalManager.scheduler.start()
        yield
        GlobalManager.scheduler.shutdown()

    def load_config(path: str) -> bool:
        if os.path.exists(path):
            with open(path, "r") as file:
                GlobalManager.global_config = Config.model_validate_json(file.read())
                return True
        else:
            GlobalManager.global_config = Config()
            return False

    def save_config(path: str):
        with open(path, "w") as file:
            file.write(GlobalManager.global_config.model_dump_json(indent = 4))

    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(description = "Automikan")
        parser.add_argument("--config", type = str, default = "/automikan/config.json", help = "Path to the configuration file")
        return parser.parse_args()

    def update_title_to_mikan_id_cache(titles: list[str], mikan_id: int):
        for title in titles: 
            GlobalManager.global_cache["title"][title] = mikan_id
    
    def build_title_to_mikan_id_cache():
        animes = Anime.select()
        for anime in animes:
            if anime.mikan_id != None:
                titles = anime.alternative_title.split("\n")
                GlobalManager.update_title_to_mikan_id_cache(titles, anime.mikan_id)
    
    def update_provider_to_mikan_id_cache(names: list[str], mikan_id: int):
        for name in names: 
            GlobalManager.global_cache["provider"][name] = mikan_id

    def build_provider_to_mikan_id_cache():
        providers = Provider.select()
        for provider in providers:
            if provider.mikan_id != None:
                names = provider.alternative_name.split("\n")
                GlobalManager.update_provider_to_mikan_id_cache(names, provider.mikan_id)
    
    def update_common_pattern(field: str, common: list[str]):
        pattern = GlobalManager.global_config.name_parse_patterns[field]
        pattern.common_pattern.extend(common)
        GlobalManager.global_cache["common_pattern"][field] = concat_re_pattern(pattern.common_pattern, pattern.reverse_match, pattern.ignore_case)

    def build_common_pattern_cache():
        for field in GlobalManager.global_config.name_parse_pattern_fields:
            pattern = GlobalManager.global_config.name_parse_patterns[field]
            GlobalManager.global_cache["common_pattern"][field] = concat_re_pattern(pattern.common_pattern, pattern.reverse_match, pattern.ignore_case)

    async def background_task():
        GlobalManager.storage.database._state._state.set(db_state_default.copy())
        GlobalManager.storage.database._state.reset()
        for manager in GlobalManager.managers:
            try:
                GlobalManager.storage.connect()
                manager.run()
            except Exception as e:
                logger.debug(e, stack_info = True, exc_info = True)
            finally:
                if not GlobalManager.storage.is_closed():
                    GlobalManager.storage.close()
            await asyncio.sleep(1)

    def reschedule():
        trigger = IntervalTrigger(minutes = GlobalManager.global_config.background_job_interval)
        GlobalManager.job.reschedule(trigger)

    def run():
        args = GlobalManager.parse_args()
        GlobalManager.config_path = args.config
        if not GlobalManager.load_config(GlobalManager.config_path):
            GlobalManager.save_config(GlobalManager.config_path)

        if GlobalManager.global_config.logging_level <= logging.DEBUG:
            logging.basicConfig(
                format = '[%(asctime)s][%(levelname)s][%(pathname)s:%(funcName)s:%(lineno)d] %(message)s',
                handlers = [
                    logging.FileHandler(GlobalManager.global_config.logging_path),
                    logging.StreamHandler()
                ],
                encoding = 'utf-8', 
                level = GlobalManager.global_config.logging_level,
            )
        else:
            logging.basicConfig(
                format='[%(asctime)s][%(levelname)s] %(message)s',
                handlers = [
                    logging.FileHandler(GlobalManager.global_config.logging_path),
                    logging.StreamHandler()
                ],
                encoding = 'utf-8', 
                level = GlobalManager.global_config.logging_level,
            )

        GlobalManager.storage = Storage(GlobalManager.global_config.database_url, GlobalManager.global_config.database_pragmas)
        GlobalManager.storage.init()

        GlobalManager.scheduler = AsyncIOScheduler()
        trigger = IntervalTrigger(minutes = GlobalManager.global_config.background_job_interval)
        GlobalManager.job = GlobalManager.scheduler.add_job(GlobalManager.background_task, trigger)

        GlobalManager.app = FastAPI(lifespan = GlobalManager.lifespan, debug = GlobalManager.global_config.return_detail_error_info)
        GlobalManager.app.add_middleware(
            CORSMiddleware,
            allow_origins = GlobalManager.global_config.CORS_origins,
            allow_credentials = True,
            allow_methods = ["*"],
            allow_headers = ["*"],
        )
        @GlobalManager.app.get("/alive")
        async def alive():
            return True