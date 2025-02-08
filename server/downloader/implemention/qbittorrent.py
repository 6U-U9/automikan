import logging
logger = logging.getLogger(__name__)

import qbittorrentapi

from storage.model import Torrent
from downloader.base_downloader import BaseDownloader
from downloader.torrent_info import TorrentInfo
from utils.string import model_to_json

class QbittorrentDownloader(BaseDownloader):
    client: qbittorrentapi.Client

    def __init__(self, connention_info: dict):
        self.client = qbittorrentapi.Client(**connention_info)
        try:
            self.client.auth_log_in()
        except qbittorrentapi.APIConnectionError as e:
            logger.error(f"Cannot connect to qbittorrent")
        except Exception as e:
            logger.debug(e, exc_info = True, stack_info = True)

    def add_torrent(self, torrent: Torrent) -> bool:
        try:
            response = self.client.torrents_add(
                torrent_files = torrent.path,
                # is_root_folder = True,
                content_layout = 'Subfolder',
            )
            if response == "Ok.":
                pass
            elif response == "Fails.":
                logger.error(f"Failed to add torrent to downloader {model_to_json(torrent)}")
                return False
            else:
                logger.error(f"Unknown response from add_torrent call")
                return False
        except Exception as e:
            logger.debug(e, exc_info = True, stack_info = True)
            return False
        # Todo: add trackers
        return True
    
    def delete_torrent(self, torrent: Torrent, delete_files = True) -> bool:
        try:
            response = self.client.torrents_delete(
                torrent_hashes = torrent.hash,
                delete_files = delete_files
            )
            if response != None:
                logger.error(f"Unknown response from add_torrent call")
                return False
        except Exception as e:
            logger.debug(e, exc_info = True, stack_info = True)
            return False
        return True
    
    def get_torrent_info(self, torrent: Torrent) -> dict | None:
        info = None
        try:
            response = self.client.torrents_info(
                torrent_hashes = torrent.hash
            )
            if len(response) != 1:
                logger.error(f"Wrong torrent info number retrieved")
        except Exception as e:
            logger.debug(e, exc_info = True, stack_info = True)
        if len(response) == 0:
            return info
        
        response = response[0]
        info = TorrentInfo(
            path = response["root_path"],
            finish = response.state_enum.is_complete
        )
        return info
