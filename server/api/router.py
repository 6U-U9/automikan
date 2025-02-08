from fastapi import FastAPI

from api import user, subscription, poster, provider, anime, anime_version, episode, episode_version, torrent, hardlink, config

def register_routers(app: FastAPI):
    app.include_router(user.router)
    app.include_router(subscription.router)
    app.include_router(poster.router)
    app.include_router(anime.router)
    app.include_router(episode.router)
    app.include_router(anime_version.router)
    app.include_router(episode_version.router)
    app.include_router(provider.router)
    app.include_router(torrent.router)
    app.include_router(hardlink.router)
    app.include_router(config.router)