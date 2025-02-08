import logging
logger = logging.getLogger(__name__)
import datetime

from storage.model import User, Subscription, Poster, Torrent, Provider, Anime, AnimeVersion, Episode, EpisodeVersion
from utils.string import model_to_json
from utils.request import Request
from manager.global_manager import GlobalManager
from parser.mikan_rss_parser import MikanRssParser
from parser.mikan_torrent_html_parser import MikanTorrentHtmlParser

# Every period of time, foreach mikan MyBangumi RSS (aggregate RSS) link in {Subscription} table
# parse Anime list from RSS, get infomation form RSS list (title, provider, resolution, video coding, audio coding, format)
# get new Anime info from web page, write into anime database
# generate detailed RSS for each new Anime by a filter, (prevent update too mach???)

class MikanAggregateRssManager():
    def get_torrent_html_info(self, episode_info, request, info):
        if episode_info != None:
            return episode_info

        episode_response = request.get(info["link"])
        episode_info = MikanTorrentHtmlParser.parse(episode_response.text)

        # update database
        poster, created = Poster.get_or_create(url = episode_info["poster"])
        
        anime, created = Anime.get_or_create(mikan_id = episode_info["mikan_bangumi_id"],
            defaults = {
                "title" : episode_info["title"],
                "alternative_title" : "\n".join(info["torrent_title"]["titles"]),
                "season" : 1 if info["torrent_title"]["season"] == None else info["torrent_title"]["season"],
                "poster" : poster
            }
        )
        
        query = list(Provider.select().where(Provider.mikan_id == episode_info["mikan_subgroup_id"]))
        if len(query) == 0:
            provider = Provider(
                mikan_id = episode_info["mikan_subgroup_id"],
                name = episode_info["mikan_subgroup_name"],
                alternative_name = episode_info["mikan_subgroup_name"]
            )
            provider.save()
        else:
            provider = query[0]
            names = provider.alternative_name.split()
            if episode_info["mikan_subgroup_name"] not in names:
                names.append(episode_info["mikan_subgroup_name"])
                provider.alternative_name = "\n".join(names)
                provider.save()
        
        return episode_info

    def add_bangumi_subgroup_rss(self, mikan_bangumi_id: int, provider_id: int):
        url = GlobalManager.global_config.mikan_bangumi_rss_template.format(mikan_bangumi_id = mikan_bangumi_id, provider_id = provider_id)
        try:
            rss, created = Subscription.get_or_create(
                        url = url,
                        source = "mikan",
                        aggregate = False,
                        defaults = {
                            "auto": True,
                            "create_time": datetime.datetime.now(),
                            "update_time": datetime.datetime.now()
                        }
                    )
            logger.info(f"Add Mikan RSS: {url}")
        except Exception as e:
            logger.error(f"Add Mikan RSS failed: {url}, {e}")

    def run(self):
        # with Storage(GlobalManager.global_config.database, GlobalManager.global_config.database_name, GlobalManager.global_config.database_pragmas) as storage:
        mybungumi_rss = list(Subscription.select().where(
            (Subscription.source == "mikan") & 
            (Subscription.aggregate == True)
        ))
        title_cache : dict = GlobalManager.global_cache.get("title")
        provider_cache : dict = GlobalManager.global_cache.get("provider")
        episode_info : dict = None
        with Request(GlobalManager.global_config.request_header, GlobalManager.global_config.proxy) as request:
            for rss in mybungumi_rss:
                rss_response = request.get(rss.url)
                rss_infos = MikanRssParser.parse(rss_response.text)
                for info in rss_infos:
                    # get anime
                    anime_id = -1
                    # for that we cache alternative titles, do not use fuzzy match here
                    for title in info["torrent_title"]["titles"]:
                        if title in title_cache:
                            anime_id = title_cache[title]
                            break
                    if anime_id == -1:
                        # get mikan id from website
                        episode_info = self.get_torrent_html_info(episode_info, request, info)
                        anime_id = episode_info["mikan_bangumi_id"]
                    for title in info["torrent_title"]["titles"]:
                        title_cache[title] = anime_id
                    anime: Anime = Anime.get(Anime.mikan_id == anime_id)
                    # get provider
                    provider_id = -1
                    if info["torrent_title"]["provider"] in provider_cache:
                        provider_id = provider_cache[info["torrent_title"]["provider"]]
                    if provider_id == -1:
                        episode_info = self.get_torrent_html_info(episode_info, request, info)
                        provider_id = episode_info["mikan_subgroup_id"]
                    provider: Provider = Provider.get(Provider.mikan_id == provider_id)
                    # get anime version
                    query = list(AnimeVersion.select().where(
                        (AnimeVersion.anime == anime) & 
                        (AnimeVersion.provider == provider) &
                        (AnimeVersion.format == info["torrent_title"]["format"]) &
                        (AnimeVersion.audio_coding == info["torrent_title"]["audio_coding"]) &
                        (AnimeVersion.video_coding == info["torrent_title"]["video_coding"]) &
                        (AnimeVersion.resolution == info["torrent_title"]["resolution"]) &
                        (AnimeVersion.source == info["torrent_title"]["source"]) &
                        (AnimeVersion.subtitle_language == info["torrent_title"]["subtitle_language"]) &
                        (AnimeVersion.subtitle_hardcoded == info["torrent_title"]["subtitle_hardcoded"])
                    ))
                    # add subscription by bangumi and subgroup 
                    self.add_bangumi_subgroup_rss(anime.mikan_id, provider.mikan_id)
                    if len(query) > 0:
                        anime_version = query[0]
                    else:
                        anime_version = AnimeVersion(
                            anime = anime,
                            provider = provider,
                            format = info["torrent_title"]["format"],
                            audio_coding = info["torrent_title"]["audio_coding"],
                            video_coding = info["torrent_title"]["video_coding"],
                            resolution = info["torrent_title"]["resolution"],
                            source = info["torrent_title"]["source"],
                            subtitle_language = info["torrent_title"]["subtitle_language"],
                            subtitle_hardcoded = info["torrent_title"]["subtitle_hardcoded"],
                        )
                        anime_version.save()
                    # torrent
                    torrent, created = Torrent.get_or_create(
                        url = info["torrent_url"],
                        defaults = {
                            "name" : info["title"],
                            "download" : False
                        }
                    )
                    # episode
                    for index in range(info["torrent_title"]["index"][0], info["torrent_title"]["index"][1] + 1):
                        episode, created = Episode.get_or_create(
                            anime = anime, 
                            index = index, 
                            special = info["torrent_title"]["special"]
                        )
                        query : list[EpisodeVersion] = list(EpisodeVersion.select().where(
                            (EpisodeVersion.version == anime_version) & 
                            (EpisodeVersion.episode == episode)
                        ))
                        if len(query) > 0:
                            logger.error(f"Duplicate version of same episode: {model_to_json(query[0])}")
                            continue
                        if len(query) == 1 and query[0].torrent != torrent:
                            logger.warning(f"Found different torrent for same episode version: {model_to_json(query[0])} found new torrent {model_to_json(torrent)}")
                            continue
                        episode_version = EpisodeVersion(
                            episode = episode,
                            version = anime_version,
                            torrent = torrent,
                            update_time = datetime.datetime.now()
                        )
                        episode_version.save()

