import logging
logger = logging.getLogger(__name__)

from downloader.base_downloader import BaseDownloader
from downloader.implemention.qbittorrent import QbittorrentDownloader

class DownloaderFactory:
    qbittorrent_downloader = None
    def get(downloader: str, connection_info: dict) -> BaseDownloader | None:
        match downloader:
            case "qbittorrent":
                if DownloaderFactory.qbittorrent_downloader == None:
                    DownloaderFactory.qbittorrent_downloader = QbittorrentDownloader(connection_info)
                return DownloaderFactory.qbittorrent_downloader
            case _:
                logger.debug(f"Downloader {type(downloader)} not implemented")
                return None