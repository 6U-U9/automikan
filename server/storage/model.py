from typing import Any
from peewee import *
import datetime

database_proxy = DatabaseProxy()
class BaseModel(Model):
    class Meta:
        database = database_proxy

class User(BaseModel):
    id = IntegerField(primary_key = True)
    name = CharField(unique = True)
    password = CharField()
    email = CharField(default = "")
    # update_time = DateTimeField(default = datetime.datetime.now())

# RSS
class Subscription(BaseModel):
    id = IntegerField(primary_key = True)
    # each type has a corresponding manager to deal with
    source = CharField(default = "mikan")
    aggregate = BooleanField(default = True)
    url = CharField(unique = True)
    
    auto = BooleanField(default = False)
    enable = BooleanField(default = True)
    
    create_time = DateTimeField(default = datetime.datetime.now())
    update_time = DateTimeField(default = datetime.datetime.now())

class Torrent(BaseModel):
    id = IntegerField(primary_key = True)
    url = CharField(unique = True, null = True)
    name = CharField(default = "")
    hash = CharField(unique = True, null = True)
    path = CharField(unique = True, null = True)
    download = BooleanField(default = False)
    
    # state
    chosen = BooleanField(default = False)
    downloading = BooleanField(default = False)
    finished = BooleanField(default = False)
    update_time = DateTimeField(default = datetime.datetime.now())

class Poster(BaseModel):
    id = IntegerField(primary_key = True)
    url = CharField(unique = True)
    path = CharField(unique = True, null = True)
    download = BooleanField(default = False)

class Provider(BaseModel):
    id = IntegerField(primary_key = True)
    mikan_id = IntegerField(unique = True, null = True)
    name = CharField(default = "")
    alternative_name = TextField(default = "")

class Anime(BaseModel):
    id = IntegerField(primary_key = True)
    mikan_id = IntegerField(unique = True, null = True)
    title = CharField(default = "")
    alternative_title = TextField(default = "")
    season = IntegerField(default = 1)
    poster = ForeignKeyField(Poster, backref = "anime")
    air_time = DateField(null = True)

    # state
    update_time = DateTimeField(default = datetime.datetime.now())
    fliter_rule = TextField(default = "")
    naming_format = TextField(default = "")
    path_naming_format = TextField(default = "")
    finished = BooleanField(default = False)

class AnimeVersion(BaseModel):
    id = IntegerField(primary_key = True)
    anime = ForeignKeyField(Anime, backref = "version")
    provider = ForeignKeyField(Provider, backref = "anime")
    format = CharField(null = True)
    audio_coding = CharField(null = True)
    video_coding = CharField(null = True)
    resolution = CharField(null = True)
    source = CharField(null = True)
    subtitle_language = CharField(null = True)
    subtitle_hardcoded = CharField(null = True)

    # state
    # update_time = DateTimeField(default = datetime.datetime.now)
    # finished = BooleanField(default = False)

class Episode(BaseModel):
    id = IntegerField(primary_key =  True)
    anime = ForeignKeyField(Anime, backref = "episode")
    index = IntegerField(default = 0)
    # when index set to 0, it is a special episode
    # example: 8.5 
    special = CharField(null = True)
    
    title = CharField(default = "")
    alternative_title = TextField(default = "")

class EpisodeVersion(BaseModel):
    id = IntegerField(primary_key = True)
    episode = ForeignKeyField(Episode, backref= "version") 
    version = ForeignKeyField(AnimeVersion, backref = "episode")
    torrent = ForeignKeyField(Torrent, backref = "file", null = True)

    # state
    update_time = DateTimeField(default = datetime.datetime.now())

class HardLink(BaseModel):
    id = IntegerField(primary_key = True)
    episode = ForeignKeyField(EpisodeVersion, backref = "hard_link")
    link_file_path = CharField(unique = True)
    origin_file_path = CharField(default = "")

### Followed is unused model
# which version to choose
class UserAnimeVersion(BaseModel):
    id = IntegerField(primary_key = True)
    user = ForeignKeyField(User, backref = "anime_version")
    anime = ForeignKeyField(AnimeVersion, backref = "user")

class UserEpisodeVersion(BaseModel):
    id = IntegerField(primary_key = True)
    user = ForeignKeyField(User, backref = "episode_version")
    episode = ForeignKeyField(EpisodeVersion, backref = "user")

class UserSubscription(BaseModel):
    id = IntegerField(primary_key = True)
    user = ForeignKeyField(User, backref = "subscription")
    subscription = ForeignKeyField(Subscription, backref = "user")

class UserHardLink(BaseModel):
    id = IntegerField(primary_key = True)
    user = ForeignKeyField(User, backref = "file")
    hard_link = ForeignKeyField(HardLink, backref = "user")