import requests

from parser.mikan_rss_parser import MikanRssParser

# Test mikan rss with bangumi id and subgroup id
# assert we get enough items for previous episode before aggregated RSS subscription 
def test_mikan_rss_bungumi_and_subgroup():
    url = "https://mikanani.me/RSS/Bangumi?bangumiId=3141&subgroupid=370"
    session = requests.Session()
    req = session.get(url = url)
    infos = MikanRssParser.parse(req.text)
    assert len(infos) > 28

if __name__ == "__main__":
    test_mikan_rss_bungumi_and_subgroup()
    pass