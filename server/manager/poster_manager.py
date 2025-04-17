import logging
logger = logging.getLogger(__name__)
import os

from utils.string import model_to_json
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
                poster.path = name
                absolute_path = os.path.join(GlobalManager.global_config.poster_directory, name)
                with open(absolute_path, "wb") as file:
                    file.write(response.content)
                poster.download = True
                poster.save()
    
    def _create_link(self):
        query : list[Poster]
        query = list(Poster.select().where((Poster.download == True) & (Poster.link == False)))
        for poster in query:
            if len(poster.anime) <= 0:
                logger.error(f"Poster {model_to_json(poster)} do not have anime")
                continue

            anime = poster.anime[0]
            path_naming_format = anime.path_naming_format
            if path_naming_format == "":
                path_naming_format = GlobalManager.global_config.global_path_naming_format
            path_name = path_naming_format.format(
                    title = anime.title,
                    season = anime.season
                )
            # Save to upper folder    
            path_name = path_name.split('/')[0]
            hard_link_directory = os.path.join(GlobalManager.global_config.bangumi_directory, path_name)
            logger.debug(f"Check {anime.title} folder structure {hard_link_directory}")
            if not os.path.exists(hard_link_directory):
                os.makedirs(hard_link_directory)
            
            absolute_path = os.path.join(GlobalManager.global_config.poster_directory, poster.path)
            link_file_path = os.path.join(hard_link_directory, poster.path)
            try:
                if os.path.exists(link_file_path):
                    os.remove(link_file_path)
                os.link(absolute_path, link_file_path)
            except Exception as e:
                logger.error(f"Unable to create hard link for {link_file_path}, please check file permissions")
                continue
            poster.link = True
            poster.save()

    def _delete(self):
        # Todo
        pass

    def run(self):
        self._download()
        self._create_link()
        self._delete()
                