import logging
logger = logging.getLogger(__name__)
import datetime
import os

from storage.model import Torrent, EpisodeVersion, HardLink
from parser.name_parser import NameParser
from parser.ai_name_parser import AiNameParser
from downloader.base_downloader import BaseDownloader
from downloader.factory import DownloaderFactory
from manager.global_manager import GlobalManager
from utils.string import model_to_json

class FileManager():
    downloader: BaseDownloader

    def __init__(self):
        self.downloader = DownloaderFactory.get(GlobalManager.global_config.downloader, GlobalManager.global_config.downloader_connection_info)

    def update_hard_link_model(self, link_file_path: str, origin_file_path: str, episode_version: EpisodeVersion):
        logger.debug(f"Link {origin_file_path} to {link_file_path}")
        try:
            if os.path.exists(link_file_path):
                os.remove(link_file_path)
                hardlink = HardLink.get_or_none(HardLink.link_file_path == link_file_path)
                if hardlink != None:
                    hardlink.delete_instance()
            os.link(origin_file_path, link_file_path)
            hardlink = HardLink(
                episode = episode_version,
                link_file_path = link_file_path,
                origin_file_path = origin_file_path
            )
            hardlink.save()
        except Exception as e:
            logger.error(f"Unable to create hard link for {link_file_path}, please check file permissions")

    def create_hard_link(self, torrent: Torrent, path: str) -> bool:
        episode_versions: list[EpisodeVersion] = torrent.file
        if len(episode_versions) == 0:
            logger.error(f"Torrent {model_to_json(torrent)} has no episode version")
            return False
        anime = episode_versions[0].episode.anime
        path_naming_format = anime.path_naming_format
        if path_naming_format == "":
            path_naming_format = GlobalManager.global_config.global_path_naming_format
        path_name = path_naming_format.format(
                title = anime.title,
                season = anime.season
            )
        hard_link_directory = os.path.join(GlobalManager.global_config.bangumi_directory, path_name)
        logger.debug(f"Check {anime.title} folder structure {hard_link_directory}")
        if not os.path.exists(hard_link_directory):
            os.makedirs(hard_link_directory)

        video_files = []
        subtitle_files = []
        for file in os.listdir(path):
            if os.path.isfile(os.path.join(path, file)):
                file_extension = file.split(".")[-1].lower()
                if file_extension in GlobalManager.global_config.name_parse_patterns["video_format"].common_pattern:
                    video_files.append(file)
                elif file_extension in GlobalManager.global_config.name_parse_patterns["subtitle_format"].common_pattern:
                    subtitle_files.append(file)

        for file in video_files:
            if GlobalManager.global_config.enable_ai_parser:
                info = AiNameParser.parse(file)
            else:
                info = NameParser.parse(file)
            index = info["index"]
            if index[0] != index[1]:
                logger.error(f"Single file {file} parse to multiple index, skip hard link")
                continue
            index = index[0]

            episode_version = None
            for temp in episode_versions:
                if temp.episode.index == index and temp.episode.special == info["special"]:
                    episode_version = temp
            if episode_version == None:
                logger.error(f"Cannot find episode version for {file}, skip hard link")
                continue

            # Todo: maybe we should check whether parsed info is same with saved info
            naming_format = anime.naming_format
            if naming_format == "":
                naming_format = GlobalManager.global_config.global_naming_format
            hard_link_base_name = naming_format.format(
                title = anime.title,
                index = episode_version.episode.index,
                special = episode_version.episode.special,
                season = anime.season,
                provider = episode_version.version.provider,
                format = episode_version.version.format,
                audio_coding = episode_version.version.audio_coding,
                video_coding = episode_version.version.video_coding,
                resolution = episode_version.version.resolution,
                source = episode_version.version.source,
                subtitle_language = episode_version.version.subtitle_language,
                subtitle_hardcoded = episode_version.version.subtitle_hardcoded
            )
            hard_link_name = hard_link_base_name + "." + file.split(".")[-1].lower()
            hard_link = os.path.join(hard_link_directory, hard_link_name)
            self.update_hard_link_model(hard_link, os.path.join(path, file), episode_version)

            for subtitle in subtitle_files:
                if subtitle.startwith(file[:file.rfind(".")]):
                    language_list = []
                    languages = subtitle.split(".")[-2].lower().split("&")
                    for language in language:
                        if language in GlobalManager.global_config.subtitle_suffix:
                            language_list.append[language]
                    if len(language_list) == 0:
                        hard_link_name = hard_link_base_name + "." + subtitle.split(".")[-1].lower()
                    else:
                        language_list.sort()
                        hard_link_name = hard_link_base_name + "." + str.join("&", language_list) + "." + subtitle.split(".")[-1].lower()
                    hard_link = os.path.join(hard_link_directory, hard_link_name)
                    self.update_hard_link_model(hard_link, os.path.join(path, file), episode_version)

        torrent.finished = True
        torrent.update_time = datetime.datetime.now()
        torrent.save()

    def run(self):
        torrents : list[Torrent]

        torrents = list(Torrent.select().where((Torrent.chosen == True) & (Torrent.downloading == True) & (Torrent.finished == False)))
        for torrent in torrents:
            torrent_info = self.downloader.get_torrent_info(torrent)
            if torrent_info and torrent_info.finish:
                self.create_hard_link(torrent, torrent_info.path)
                logger.info(f"Create hard link for {torrent.name}")
