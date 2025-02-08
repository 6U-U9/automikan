import uvicorn
from manager.global_manager import GlobalManager
from api import user, subscription, poster, provider, anime, anime_version, episode, episode_version, torrent, hardlink, config
from manager.mikan_aggregate_rss_manager import MikanAggregateRssManager
from manager.mikan_bangumi_rss_manager import MikanBangumiRssManager
from manager.poster_manager import PosterManager
from manager.version_manager import VersionManager
from manager.torrent_manager import TorrentManager
from manager.download_manager import DownloadManager
from manager.file_manager import FileManager

if __name__ == "__main__":
    GlobalManager.run()
    GlobalManager.managers.append(MikanAggregateRssManager())
    GlobalManager.managers.append(MikanBangumiRssManager())
    GlobalManager.managers.append(PosterManager())
    GlobalManager.managers.append(VersionManager())
    GlobalManager.managers.append(TorrentManager())
    GlobalManager.managers.append(DownloadManager())
    GlobalManager.managers.append(FileManager())
    GlobalManager.app.include_router(user.router)
    GlobalManager.app.include_router(subscription.router)
    GlobalManager.app.include_router(poster.router)
    GlobalManager.app.include_router(anime.router)
    GlobalManager.app.include_router(episode.router)
    GlobalManager.app.include_router(anime_version.router)
    GlobalManager.app.include_router(episode_version.router)
    GlobalManager.app.include_router(provider.router)
    GlobalManager.app.include_router(torrent.router)
    GlobalManager.app.include_router(hardlink.router)
    GlobalManager.app.include_router(config.router)
    uvicorn.run(
        GlobalManager.app, 
        host = GlobalManager.global_config.host, 
        port = GlobalManager.global_config.port,
    )