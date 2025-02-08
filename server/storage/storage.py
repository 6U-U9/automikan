### Instructions from openapi 
### https://fastapi.xiniushu.com/uk/advanced/sql-databases-peewee/
import peewee
from contextvars import ContextVar
db_state_default = {"closed": None, "conn": None, "ctx": None, "transactions": None}
db_state = ContextVar("db_state", default = db_state_default.copy())
class PeeweeConnectionState(peewee._ConnectionState):
    def __init__(self, **kwargs):
        super().__setattr__("_state", db_state)
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        self._state.get()[name] = value

    def __getattr__(self, name):
        return self._state.get()[name]
###
###

from typing import Any
from peewee import *   
from playhouse import db_url

from storage.model import User, Subscription, Poster, Torrent, Provider, Anime, AnimeVersion, Episode, EpisodeVersion, HardLink, UserAnimeVersion, UserEpisodeVersion, UserSubscription, UserHardLink
from storage.model import database_proxy

class Storage():
    database: Database

    def __init__(self, database_url: str, pragmas: dict[str, Any]):
        self.database = db_url.connect(database_url, pragmas)
        self.database._state = PeeweeConnectionState()
        database_proxy.initialize(self.database)
        
    def init(self):
        self.database.connect(reuse_if_open=True)
        self.database.create_tables([User, Subscription, Poster, Torrent, Provider, Anime, AnimeVersion, Episode, EpisodeVersion, HardLink, UserAnimeVersion, UserEpisodeVersion, UserSubscription, UserHardLink])
        self.database.close()

    def connect(self) -> bool:
        return self.database.connect(reuse_if_open=True)

    def close(self) -> bool:
        return self.database.close()

    def is_closed(self) -> bool:
        return self.database.is_closed()

    def __enter__(self):
        self.init()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
