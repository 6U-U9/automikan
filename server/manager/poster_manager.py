import logging
logger = logging.getLogger(__name__)
import os

from storage.model import Poster
from manager.global_manager import GlobalManager
from utils.request import Request

class PosterManager():
    def _download(self):
        query : list[Poster]
        query = list(Poster.select().where(Poster.download == False))

        with Request(GlobalManager.global_config.request_header, GlobalManager.global_config.proxy) as request:
            for poster in query:
                response = request.get(poster.url)
                if response == None:
                    logger.warning(f"Failed download poster: {poster.url}")
                    continue
                image_format = poster.url.split('.')[-1]
                name = poster.url.split('/')[-1]
                if len(poster.anime) > 0:
                    name = poster.anime[0].title + f".{image_format}"
                poster.path = os.path.join(GlobalManager.global_config.poster_directory, name)
                with open(poster.path, "wb") as file:
                    file.write(response.content)
                poster.download = True
                poster.save()

    def _delete(self):
        # Todo
        pass

    def run(self):
        self._download()
        self._delete()
                