import os

from manager.global_manager import GlobalManager
from storage.storage import Storage
from storage.model import User, Subscription, Poster, Torrent, Provider, Anime, AnimeVersion, Episode, EpisodeVersion
from manager.mikan_aggregate_rss_manager import MikanAggregateRssManager
from manager.mikan_bangumi_rss_manager import MikanBangumiRssManager
from manager.poster_manager import PosterManager
from manager.torrent_manager import TorrentManager
from manager.version_manager import VersionManager
from manager.download_manager import DownloadManager

def test_mikan():
    os.remove(GlobalManager.global_config.database_url)
    storage = Storage(GlobalManager.global_config.database, GlobalManager.global_config.database_url, GlobalManager.global_config.database_pragmas)
    storage.init()
    # Data init
    admin = User(name="admin", password = "password", email = "admin@local.test")
    admin.save()
    # Todo: change this url
    rss = Subscription(url = "https://mikanani.me/RSS/MyBangumi?token=***", user = admin)
    rss.save()

    mikan_aggregate_rss_manager =  MikanAggregateRssManager()
    mikan_bangumi_rss_manager = MikanBangumiRssManager()
    poster_manager = PosterManager()
    torrent_manager = TorrentManager()
    version_manager = VersionManager()
    download_manager = DownloadManager()

    mikan_aggregate_rss_manager.run()
    mikan_bangumi_rss_manager.run()
    poster_manager.run()
    version_manager.run()
    torrent_manager.run()
    download_manager.run()
    # Todo: filemanager

    storage.close()

if __name__ == "__main__":
    test_mikan()
    pass