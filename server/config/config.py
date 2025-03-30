import logging
import datetime
from typing import Any
from pydantic import BaseModel

from utils.string import generate_base64_key

class Pattern(BaseModel):
    common_pattern: list[str] | None = None
    unknown_pattern: str | None = None
    reverse_match: bool = False
    ignore_case: bool = False

class Config(BaseModel):
    # Logging
    logging_path: str = "/automikan/automikan.log"
    logging_level: int = logging.DEBUG
    return_detail_error_info: bool = True
    enable_api_doc: bool = False

    # User (Not implemented yet)
    single_user: bool = False

    # API
    host: str = "0.0.0.0"
    port: int = 8236
    CORS_origins: list[str] = [
        "*",
    ]
    jwt_secret_key: str = generate_base64_key()
    jwt_algorithm: str = "HS256"

    # Torrent
    torrent_directory: str = "/torrents"
    save_all_torrent: bool = False # save every ".torrent" file seen
    delete_unreferenced_torrent: bool = False # delete unreferenced torrent

    # Mikan
    mikan_bangumi_rss_template: str = r"https://mikanime.tv/RSS/Bangumi?bangumiId={mikan_bangumi_id}&subgroupid={provider_id}"

    # Download
    bangumi_directory: str = "/bangumi"
    poster_directory: str = "/automikan/poster"
    global_path_naming_format: str = r"{title}/Season {season:02d}"
    global_naming_format: str = r"{title} - S{season:02d}E{index:02d}"
    select_by_episode: bool = True # False: select_by_anime
    remove_covered_download: bool = True # Remove download which has a better version
    background_job_interval: int = 30 # Minutes
    version_check_timeout: datetime.timedelta = datetime.timedelta(days = 14)

    # Downloader
    downloader: str = "qbittorrent"
    downloader_connection_info: dict[str, str] = {
        "host": "http://qbittorrent-automikan:8080",
        "username": "admin",
        "password": "password",
        #"VERIFY_WEBUI_CERTIFICATE": False,
    }
    
    # Network
    proxy: str | None = None
    request_header: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Cache-Control": "no-cache",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    }
    
    # Database
    database_url: str = "sqlite:////automikan/automikan.db"
    database_pragmas: dict[str, Any] = {
        "journal_mode": 'wal', 
        "cache_size": -1 * 64 * 1024, 
        "foreign_keys": 1,
        "check_same_thread": False
    }

    # Pattern
    add_name_parse_result_to_common: bool = True
    # special for title
    name_parse_pattern_fields: list[str] = [
        "provider", 
        "season",
        "multiple_index", 
        "single_index", 
        "video_format", 
        "subtitle_format", 
        "subtitle_language", 
        "subtitle_hardcoded", 
        "video_coding", 
        "audio_coding", 
        "source", 
        "resolution", 
        "special", 
    ]
    name_parse_patterns: dict[str, Pattern] = {
        "provider": Pattern(
            common_pattern = None,
            unknown_pattern = r'(?i)\[(.*?)\]|\【(.*?)\】',
            reverse_match = False,
            ignore_case = False,
        ), 
        "season": Pattern(
            common_pattern = None,
            unknown_pattern = r'(?i)(\d+)[nd, rd, th] Season|第\s*(\d+)\s*季|S(\d+)',
            reverse_match = False,
            ignore_case = False,
        ),# Todo
        "multiple_index": Pattern(
            common_pattern = None,
            unknown_pattern = r'(?i)\[(\d+)\s*-\s*(\d+)\]|\[(\d+)\s*-\s*(\d+)\s*合集\]',
            reverse_match = False,
            ignore_case = True,
        ), 
        "single_index": Pattern(
            common_pattern = None,
            unknown_pattern = r'(?i)\s*-\s*(\d+)\s*|\[(\d+)\]|第\s*(\d+)\s*集|E(\d+)',
            reverse_match = False,
            ignore_case = True,
        ), 
        "video_format": Pattern(
            common_pattern = ["mkv", "mp4"],
            unknown_pattern = None,
            reverse_match = True,
            ignore_case = False,
        ), 
        "subtitle_format": Pattern(
            common_pattern = ["ass", "srt"],
            unknown_pattern = None,
            reverse_match = True,
            ignore_case = False,
        ), 
        "subtitle_language": Pattern(
            common_pattern = ["chs", "cht", "jp"],
            unknown_pattern = r'(?ri)([简|繁|日][简|繁|日]{0,1}[简|繁|日]{0,1})',
            reverse_match = True,
            ignore_case = True,
        ), 
        "subtitle_hardcoded": Pattern(
            common_pattern = ["内嵌", "内封", "外挂"],
            unknown_pattern = None,
            reverse_match = True,
            ignore_case = False,
        ), 
        "video_coding": Pattern(
            common_pattern = ["HEVC", "AVC", "H265", "H264"],
            unknown_pattern = None,
            reverse_match = True,
            ignore_case = True,
        ), 
        "audio_coding": Pattern(
            common_pattern = ["AAC", "FLAC"],
            unknown_pattern = None,
            reverse_match = True,
            ignore_case = True,
        ), 
        "source": Pattern(
            common_pattern = ["WebRip", "Baha", "B-Global", "ABEMA", "CR"],
            unknown_pattern = None,
            reverse_match = True,
            ignore_case = True,
        ), 
        "resolution": Pattern(
            common_pattern = None,
            unknown_pattern = r'(?ri)(\d{3,4}x\d{3,4})|([1-9]\d{2,3}[pP])|([1-9][kK])',
            reverse_match = True,
            ignore_case = False,
        ), 
        "special": Pattern(
            common_pattern = None,
            unknown_pattern = r'(?ri)(OVA\d*)|(OAD\d*)|\s*-\s*(\d+\.5)\s*|\[(\d+\.5)\]',
            reverse_match = False,
            ignore_case = False,
        ), 
    }

    pattern_title_exclude_front: list[str] | None = [
        r"★.*新番.*★", # for 喵萌
    ]
    pattern_title_exclude_back: list[str] | None = []
    pattern_title_exclude_char: str = r"[](){}【】|"
    subtitle_suffix: list[str] = ["sc", "tc", "chs", "cht", "en", "jp"]

    # AI
    enable_ai_parser: bool = False
    ai_proxy_url: str | None = None
    ai_api_key: str | None = None
    ai_base_url: str | None = None
    ai_model: str | None = None
    ai_prompt: str | None = r"""You are a tools to parse information from file name of animes or subtitles. You should return informations in json format.
These are the infomations you need to get from text:
1. provider: the group name that provide this anime. If you don't see this infomation, just ignore this key in json.
2. title: the title of this anime. A file name may contains mutiple titles, and they are usually divided by "/", please return this field in list.
3. season: the season of this anime. You should return a number, if there is no season infomation, return 1.
4. index: the episode index of this anime. Usually index is following titles. A name may have multiple indexes, for 01-13, you shall return a list contains two numbers [1, 13]. And for single index, you shall return a list containes two same number.
5. resolution: the resolution of this anime. You have to convert this to a list contains two numbers, such as [1920, 1080]. If you don't see this infomation, just ignore this key in json.
6. audio_coding: the audio coding of this anime. If you don't see this infomation, just ignore this key in json.
7. video_coding: the video coding of this anime. If you don't see this infomation, just ignore this key in json.
8. format: the file extension of this file. This MUST comes from the end of the name, following a dot ".", not from infomations in any bracket. If you don't see a file extension, just ignore this key in json.
9. source: where do this file comes from. If you don't see this infomation, just ignore this key in json.
10. subtitle_language: the subtitle language of this anime. You have to convert it to standard language name like "English", "Japanese", "Simplified Chinese" or "Traditional Chinese". If you don't see this infomation, just ignore this key in json.
11. subtitle_hardcoded: whether the subtitle is hardcoded or not. If you don't see this infomation, just ignore this key in json.
12. special: if the episode is special episode, please set index to [0, 0] and special contains the infomation of special episode, such as "8.5". If you don't see this infomation, just ignore this key in json.

Below are some examples for you to get a better understanding:
1. input: [Up to 21°C] 在地下城寻求邂逅是否搞错了什么 第五季 / Dungeon ni Deai wo Motomeru no wa Machigatteiru Darou ka V - 11 (CR 1920x1080 AVC AAC MKV)
output: {
    "provider": "Up to 21°C",
    "title": ["在地下城寻求邂逅是否搞错了什么", "Dungeon ni Deai wo Motomeru no wa Machigatteiru Darou ka"],
    "season": 5,
    "index": [11, 11],
    "resolution": [1920, 1080],
    "audio_coding": "AAC",
    "video_coding": "AVC",
    "source": "CR"
}
2. input: [Up to 21°C] 鸭乃桥论的禁忌推理 / Kamonohashi Ron no Kindan Suiri 2nd Season - 25 (Baha 1920x1080 AVC AAC MP4)[383.17 MB].cht.ass
output: {
    "provider": "Up to 21°C",
    "title": ["鸭乃桥论的禁忌推理", "Kamonohashi Ron no Kindan Suiri"],
    "season": 2,
    "index": [25, 25],
    "resolution": [1920, 1080],
    "audio_coding": "AAC",
    "video_coding": "AVC",
    "format": "ass",
    "source": "Baha",
    "subtitle_language": ["Traditional Chinese"]
}
3. input: [桜都字幕组] 在地下城寻求邂逅是否搞错了什么 第五季 / Dungeon ni Deai o Motomeru no wa Machigatte Iru Darouka： Familia Myth V [11][1080p][简繁内封]
output: {
    "provider": "桜都字幕组",
    "title": ["在地下城寻求邂逅是否搞错了什么", "Dungeon ni Deai o Motomeru no wa Machigatte Iru Darouka： Familia Myth"],
    "season": 5,
    "index": [11, 11],
    "resolution": [1920, 1080],
    "subtitle_language": ["Simplified Chinese", "Traditional Chinese"],
    "subtitle_hardcoded": false
}
4. input: 【喵萌奶茶屋】★10月新番★[Chi。-关于地球的运动- / Chi. Chikyuu no Undou ni Tsuite][12][1080p][繁日双语][招募翻译]
output: {
    "provider": "喵萌奶茶屋",
    "title": ["Chi。-关于地球的运动-", "Chi. Chikyuu no Undou ni Tsuite"],
    "season": 1,
    "index": [12, 12],
    "resolution": [1920, 1080],
    "subtitle_language": ["Traditional Chinese", "Japanese"]
}
5. input: [喵萌奶茶屋&LoliHouse] 物语系列 / Monogatari Series: Off & Monster Season - 02 抚物语 [WebRip 1080p HEVC-10bit AAC ASSx2][简繁日内封字幕]
output: {
    "provider": "喵萌奶茶屋&LoliHouse",
    "title": ["物语系列", "Monogatari Series"],
    "season": 1,
    "index": [2, 2],
    "resolution": [1920, 1080],
    "audio_coding": "AAC",
    "video_coding": "HEVC",
    "source": "WebRip",
    "subtitle_language": ["Simplified Chinese", "Traditional Chinese", "Japanese"],
    "subtitle_hardcoded": false
}
6. input: [LoliHouse] S级怪兽《贝希摩斯》被误认成小猫，成为精灵女孩的骑士（宠物）一起生活 / Beheneko - 01 [WebRip 1080p HEVC-10bit AAC][简繁内封字幕]
output: {
    "provider": "LoliHouse",
    "title": ["S级怪兽《贝希摩斯》被误认成小猫，成为精灵女孩的骑士（宠物）一起生活", "Beheneko"],
    "season": 1,
    "index": [1, 1],
    "resolution": [1920, 1080],
    "audio_coding": "AAC",
    "video_coding": "HEVC",
    "source": "WebRip",
    "subtitle_language": ["Simplified Chinese", "Traditional Chinese"],
    "subtitle_hardcoded": false
}
7. input: [Up to 21°C] 最狂辅助职业【话术士】世界最强战团听我号令 / Saikyou no Shienshoku 'Wajutsushi' - 12 (ABEMA 1920x1080 AVC AAC MP4)
output: {
    "provider": "Up to 21°C",
    "title": ["最狂辅助职业【话术士】世界最强战团听我号令", "Saikyou no Shienshoku 'Wajutsushi'"],
    "season": 1,
    "index": [12, 12],
    "resolution": [1920, 1080],
    "audio_coding": "AAC",
    "video_coding": "AVC",
    "format": "MP4",
    "source": "ABEMA"
}
8. input: [S1百综字幕组] GIRLS BAND CRY - S2 [13][WebRip][x265_EAC3][简繁内封][v2].srt
output: {
    "provider": "S1百综字幕组",
    "title": ["GIRLS BAND CRY"],
    "season": 2,
    "index": [13, 13],
    "audio_coding": "EAC3",
    "video_coding": "HEVC",
    "format": "srt",
    "source": "WebRip",
    "subtitle_language": ["Simplified Chinese", "Traditional Chinese"],
    "subtitle_hardcoded": false
}
9. input: [北宇治字幕组] GIRLS BAND CRY [01-13 修正合集][WebRip][HEVC_AAC][简体内嵌]
output: {
    "provider": "北宇治字幕组",
    "title": ["GIRLS BAND CRY"],
    "season": 1,
    "index": [1, 13],
    "audio_coding": "AAC",
    "video_coding": "HEVC",
    "source": "WebRip",
    "subtitle_language": ["Simplified Chinese"],
    "subtitle_hardcoded": true
}
10. input: [7³ACG&❀拨雪寻春❀] 不时用俄语小声说真心话的邻桌艾莉同学/Tokidoki Bosotto Russia Go S01 | 01-12 [简繁字幕] BDrip 1080p x265 FLAC 2.0
output: {
    "provider": "7³ACG&❀拨雪寻春❀",
    "title": ["不时用俄语小声说真心话的邻桌艾莉同学", "Tokidoki Bosotto Russia Go"],
    "season": 1,
    "index": [1, 12],
    "resolution": [1920, 1080],
    "audio_coding": "FLAC",
    "video_coding": "HEVC",
    "source": "BDrip",
    "subtitle_language": ["Simplified Chinese", "Traditional Chinese"]
}
11. input: [DBD-Raws][不时轻声地以俄语遮羞的邻座艾莉同学/Tokidoki Bosotto Rossiya-go de Dereru Tonari no Alya-san/时々ボソッとロシア语でデレる隣のアーリャさん][01-08TV][BOX1-2][1080P][BDRip][HEVC-10bit][FLAC][MKV]
output: {
    "provider": "DBD-Raws",
    "title": ["不时轻声地以俄语遮羞的邻座艾莉同学", "Tokidoki Bosotto Rossiya-go de Dereru Tonari no Alya-san", "时々ボソッとロシア语でデレる隣のアーリャさん"],
    "season": 1,
    "index": [1, 8],
    "resolution": [1920, 1080],
    "audio_coding": "FLAC",
    "video_coding": "HEVC",
    "format": "MKV",
    "source": "BDRip"
}
12. input: [桜都字幕组] 86 -不存在的战区- / 86—Eitishikkusu— [18.5][720p@60FPS][简体内嵌]
output: {
    "provider": "桜都字幕组",
    "title": ["86 -不存在的战区-", "86—Eitishikkusu—"],
    "season": 1,
    "index": [0, 0],
    "resolution": [1280, 720],
    "subtitle_language": ["Simplified Chinese"],
    "subtitle_hardcoded": true,
    "special": "18.5"
}
13: input: [天月搬运组] 无意间变成狗，被喜欢的女生捡回家。 / Inu ni Nattara Suki na Hito ni Hirowareta. - 14(OVA2) [1080P][简繁日外挂]
output: {
    "provider": "天月搬运组",
    "title": ["无意间变成狗，被喜欢的女生捡回家。", "Inu ni Nattara Suki na Hito ni Hirowareta."],
    "season": 1,
    "index": [0, 0],
    "special": "OVA2",
    "resolution": [1920, 1080],
    "subtitle_language": ["Simplified Chinese", "Traditional Chinese", "Japanese"],
    "subtitle_hardcoded": false
}
"""

    # Fliter
    default_fliter_rule: dict[str, Any] = {
        "remain": 1,
        "rules": [
            {   
                "type": "exclude",
                "field": "resolution",
                "value": "720",
                "operator": "has"
            }, {
                "type": "exclude",
                "field": "subtitle_language",
                "value": "繁",
                "operator": "has"
            }
        ]
    }

