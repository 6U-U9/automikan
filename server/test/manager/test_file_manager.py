import pytest
import os
import shutil

from manager.global_manager import GlobalManager
from storage.storage import Storage
from storage.model import Torrent, Poster, Provider, Anime, AnimeVersion, Episode, EpisodeVersion
from manager.file_manager import FileManager

class Test_File_Manager:
    def setup_class(self):
        if not os.path.exists("/tmp/automikan"):
            os.makedirs("/tmp/automikan")
            os.makedirs("/tmp/automikan/bangumi")
        GlobalManager.global_config.database_url = "/tmp/automikan/automikan-test.db"
        GlobalManager.global_config.bangumi_directory = "/tmp/automikan/bangumi"
        GlobalManager.global_config.global_naming_format = r"{title} - S{season:02d}E{index:02d}"
        GlobalManager.global_config.common_language = ["sc", "tc", "chs", "cht", "en", "jp"]
        GlobalManager.global_config.common_video_format = ["mkv", "mp4"]
        GlobalManager.global_config.common_subtitle_format = ["ass", "srt"]
        storage = Storage(GlobalManager.global_config.database, GlobalManager.global_config.database_url, GlobalManager.global_config.database_pragmas)
        storage.init()

    def teardown_class(self):
        os.remove(GlobalManager.global_config.database_url)
        shutil.rmtree("/tmp/automikan")

    def test_single_episode(self):
        poster = Poster(
            url = "url"
        )
        provider = Provider(
            mikan_id = 382,
            name = "喵萌奶茶屋"
        )
        anime = Anime(
            mikan_id = 3488,
            title = "地。-关于地球的运动-",
            season = 1,
            poster = poster
        )
        anime_version = AnimeVersion(
            anime = anime,
            provider = provider
        )
        episode = Episode(
            anime = anime,
            index = 6,
        )
        torrent = Torrent(
            hash = "469a46aa6e5dae02c8043e1efd4af2dc23407787",
            download = True,
            chosen = True,
            downloading = True,
            finished = False
        )
        episode_version = EpisodeVersion(
            episode = episode,
            version = anime_version,
            torrent = torrent,
        )
        poster.save()
        provider.save()
        torrent.save()
        anime.save()
        anime_version.save()
        episode.save()
        episode_version.save()

        file_manager = FileManager()
        file_manager.run()

        name = f"{anime.title} - S{anime.season:02d}E{episode.index:02d}.mkv"
        assert os.path.exists(os.path.join(GlobalManager.global_config.bangumi_directory, anime.title, name))

if __name__ == "__main__":
    pytest.main(["-v", f"{__file__}"])
    pass