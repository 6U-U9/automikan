import logging
logger = logging.getLogger(__name__)
import os
import datetime

from storage.model import Torrent
from manager.global_manager import GlobalManager
from utils.request import Request
from utils.torrent import get_torrent_info_hash

class TorrentManager():
    def _download(self):
        query : list[Torrent]
        if GlobalManager.global_config.save_all_torrent:
            query = Torrent.select().where(Torrent.download == False)
        else:
            query = Torrent.select().where((Torrent.chosen == True) & (Torrent.download == False))
        
        with Request(GlobalManager.global_config.request_header, GlobalManager.global_config.proxy) as request:
            for torrent in query:
                response = request.get(torrent.url)
                # prevent title contain illegal character
                name = torrent.name.replace("/", "／")
                torrent.path = os.path.join(GlobalManager.global_config.torrent_directory, name + ".torrent")
                with open(torrent.path, "wb") as file:
                    file.write(response.content)
                torrent.download = True
                torrent.update_time = datetime.datetime.now()
                torrent.hash = get_torrent_info_hash(response.content)
                torrent.save()

    def _delete(self):
        if GlobalManager.global_config.delete_unreferenced_torrent:
            query = Torrent.select().where((Torrent.chosen == False) & (Torrent.download == True))
            for torrent in query:
                os.remove(torrent.path)
                torrent.download = False
                torrent.update_time = datetime.datetime.now
                torrent.save()

    def run(self):
        self._download()
        self._delete()
                