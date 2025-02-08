import logging
logger = logging.getLogger(__name__)
import datetime

from storage.model import Torrent
from downloader.base_downloader import BaseDownloader
from downloader.factory import DownloaderFactory
from manager.global_manager import GlobalManager

# select all torrents and add to downloader
class DownloadManager():
    downloader: BaseDownloader

    def __init__(self):
        self.downloader = DownloaderFactory.get(GlobalManager.global_config.downloader, GlobalManager.global_config.downloader_connection_info)

    def run(self):
        torrents : list[Torrent]

        # Add torrent to downloader
        torrents = Torrent.select().where((Torrent.chosen == True) & (Torrent.download == True) & (Torrent.downloading == False))
        for torrent in torrents:
            logger.debug(f"Add torrent {torrent.path} to downloader")
            response = self.downloader.add_torrent(torrent)
            if response:
                torrent.downloading = True
                torrent.update_time = datetime.datetime.now()
                torrent.save()

        # Remove unwanted download
        if GlobalManager.global_config.remove_covered_download:
            torrents = Torrent.select().where((Torrent.chosen == False) & (Torrent.downloading == True))
            for torrent in torrents:
                logger.debug(f"Remove torrent {torrent.path} from downloader")
                response = self.downloader.delete_torrent(torrent)
                if response:
                    torrent.downloading = False
                    torrent.finished = False
                    torrent.update_time = datetime.datetime.now()
                    torrent.save()

        # Todo: check if any torrent is dead and choose alternative torrent for it 
        pass