import logging
logger = logging.getLogger(__name__)

from storage.model import Torrent
from downloader.torrent_info import TorrentInfo

class BaseDownloader():
    def __init__(self):
        pass

    def add_torrent(self, torrent: Torrent) -> bool:
        logger.debug(f"Call function of BaseDownloader")
        return False
    
    def delete_torrent(self, torrent: Torrent, delete_files = True) -> bool:
        logger.debug(f"Call function of BaseDownloader")
        return False
    
    def get_torrent_info(self, torrent: Torrent) -> TorrentInfo | None:
        logger.debug(f"Call function of BaseDownloader")
        return None