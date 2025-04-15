
import bs4 as bs
import regex as re
from datetime import datetime

from parser import Parser
from parser.name_parser import NameParser

date_format = '%Y/%m/%d %H:%M'
mikan_root = r"https://mikanani.me"

# Parse Torrent link
# Example: https://mikanani.me/Home/Episode/fe21ddd1a097153a81b57849a8b3608457093497
class MikanTorrentHtmlParser(Parser):
    def parse(content: str | bytes):
        info = {}
        soup = bs.BeautifulSoup(content, "lxml")
        temp = soup.css.select(".bangumi-poster")[0]['style']
        pattern = r"url\('([^']+)'\)"
        match = re.search(pattern, temp)
        poster = ""
        if match:
            poster = match.group(1).split("?")[0]
        title = soup.css.select(".bangumi-title")[0].a.text
        mikan_bangumi_url = soup.css.select(".bangumi-title")[0].a["href"]
        mikan_bangumi_id = mikan_bangumi_url.split("/")[3].split("#")[0]
        mikan_subgroup_id = mikan_bangumi_url.split("/")[3].split("#")[1]
        ## For multiple subgroups, html is different than single one
        ## For unknown subgroup, there is more to do: https://mikanani.me/Home/Episode/9624819e166b9798a7ee6d92c8ea6f17d2c84852
        mikan_subgroup_name_components = soup.css.select(".magnet-link-wrap")
        if len(mikan_subgroup_name_components) == 1:
            mikan_subgroup_name = mikan_subgroup_name_components[0].text.strip()
        else:
            mikan_subgroup_name = ""
        ## Do not parse because it will get something like "昨天 10:01"
        # torrent_publish_time = datetime.strptime(soup.css.select(".bangumi-info")[1].text.split("：")[1], date_format)

        info["poster"] = mikan_root + poster
        info["title"] = title
        info["mikan_bangumi_url"] = mikan_root + mikan_bangumi_url
        info["mikan_bangumi_id"] = mikan_bangumi_id
        info["mikan_subgroup_id"] = mikan_subgroup_id
        info["mikan_subgroup_name"] = mikan_subgroup_name
        # info["torrent_publish_time"] = torrent_publish_time

        return info

if __name__ == "__main__":
    import requests
    url_multi_subgroups = "https://mikanani.me/Home/Episode/29fefa115abf38fcfe697d7212a470b40814b958"
    url_single_subgroups = "https://mikanani.me/Home/Episode/80220ac32c48d24ebf82821f964542feacadfa18"
    session = requests.Session()
    req = session.get(url = url)
    print(MikanTorrentHtmlParser.parse(req.text))