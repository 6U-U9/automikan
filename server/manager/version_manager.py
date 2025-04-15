import logging
logger = logging.getLogger(__name__)
import datetime

from utils.string import model_to_json
from storage.model import Anime, AnimeVersion, Episode, EpisodeVersion
from manager.global_manager import GlobalManager
from fliter.fliter import Fliter

class VersionManager():
    def _select_by_episode(self, anime: Anime, fliter: Fliter):
        episodes = list(Episode.select().where(Episode.anime == anime))
        for episode in episodes:
            episode_versions = list(EpisodeVersion.select().where(EpisodeVersion.episode == episode))
            versions = [episode_version.version for episode_version in episode_versions]
            chosens = fliter.filter(versions)
            chosen_index = set([version[0] for version in chosens])
            for index, version in enumerate(episode_versions):
                if index in chosen_index:
                    episode_versions[index].torrent.chosen = True
                    logger.debug(f"Choose Version: {model_to_json(episode_versions[index])}")
                else:
                    episode_versions[index].torrent.chosen = False
                episode_versions[index].torrent.save()
    
    def _select_by_anime(self, anime: Anime, fliter: Fliter):
        versions = list(AnimeVersion.select().where(AnimeVersion.anime == anime))
        chosen_versions = [version[1] for version in fliter.filter(versions)]
        episodes = list(Episode.select().where(Episode.anime == anime))
        for episode in episodes:
            episode_versions = list(EpisodeVersion.select().where(EpisodeVersion.episode == episode))
            for version in episode_versions:
                if version.version in chosen_versions:
                    version.torrent.chosen = True
                else:
                    version.torrent.chosen = False
                version.torrent.save()

    def run(self):
        animes : list[Anime]
        animes = Anime.select().where(Anime.update_time > datetime.datetime.now() - GlobalManager.global_config.version_check_timeout)
        for anime in animes:
            fliter = Fliter(anime.fliter_rule)
            if GlobalManager.global_config.select_by_episode:
                self._select_by_episode(anime, fliter)
            else:
                self._select_by_anime(anime, fliter)
