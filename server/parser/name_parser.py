import logging
logger = logging.getLogger(__name__)
import regex as re

from parser import Parser
from config.config import Pattern
from manager.global_manager import GlobalManager
from utils.string import concat_re_pattern, list_to_string

class NameParser(Parser):
    def is_exclude_char(c: str):
        return c.isspace() or (c in GlobalManager.global_config.pattern_title_exclude_char)
    
    def fix_brackets(input_str: str):
        bracket_pairs = {
            '(': ')',
            '[': ']',
            '{': '}',
        }
        stack = []

        for char in input_str:
            if char in bracket_pairs: 
                stack.append(char)
            elif char in bracket_pairs.values(): 
                if stack and stack[-1] in bracket_pairs and bracket_pairs[stack[-1]] == char:
                    stack.pop() 
                else:
                    stack.append(char)

        left_to_add = []
        right_to_add = []

        for char in stack:
            if char in bracket_pairs: 
                right_to_add.append(bracket_pairs[char])
            elif char in bracket_pairs.values(): 
                left_to_add.append(
                    list(bracket_pairs.keys())[list(bracket_pairs.values()).index(char)]
                )

        return ''.join(left_to_add) + input_str + ''.join(right_to_add)
    
    def match_field(field: str, content: str):
        pattern = GlobalManager.global_config.name_parse_patterns[field]
        if pattern.common_pattern:
            common_pattern = concat_re_pattern(pattern.common_pattern, pattern.reverse_match, pattern.ignore_case)
            match = re.search(common_pattern, content)
            if match:
                groups = [g for g in match.groups() if g is not None]
                return groups, match.start(), match.end()
        if pattern.unknown_pattern:
            match = re.search(pattern.unknown_pattern, content)
            if match:
                groups = [g for g in match.groups() if g is not None]
                return groups, match.start(), match.end()
        return None, None, None
    
    # provider: first content inside [] or 【】
    def match_provider(content: str, start: int, end: int) -> tuple[str, int, int]:
        match, left, right = NameParser.match_field("provider", content)
        if match != None:
            provider = match[0]
            start = max(start, right)
            return provider, start, end
        return None, start, end
    
    # multiple index: "01-99"
    # single index: "- 13" or "[22]" or "E03" or "第04集"
    def match_index(content: str, start: int, end: int) -> tuple[tuple[int, int], int, int]:
        match, left, right = NameParser.match_field("multiple_index", content)
        if match != None:
            index_start = int(match[0])
            index_end = int(match[1])
            end = min(end, left)
            return (index_start, index_end), start, end
        
        match, left, right = NameParser.match_field("single_index", content)
        if match != None:
            index_start = int(match[0])
            index_end = int(match[0])
            end = min(end, left)
            return (index_start, index_end), start, end
        logger.warning(f"Parse name {content} failed, can not find index, set default episode index to 0")
        return (0, 0), start, end
    
    # resolution: 1920x1080 or 1080p or 4K
    def match_resolution(content: str, start: int, end: int) -> tuple[str, int, int]:
        match, left, right = NameParser.match_field("resolution", content)
        if match != None:
            # Todo: convert to standard format like 1920x1080
            resolution = match[0]
            end = min(end, left)
            return resolution, start, end
        logger.info(f"Parse name {content} failed, can not find resolution")
        return None, start, end
    
    # audio_coding: AAC
    def match_audio_coding(content: str, start: int, end: int) -> tuple[str, int, int]:
        match, left, right = NameParser.match_field("audio_coding", content)
        if match != None:
            # Todo: convert to standard format
            audio_coding = match[0]
            end = min(end, left)
            return audio_coding, start, end
        logger.info(f"Parse name {content} failed, can not find audio coding")
        return None, start, end
    
    # video_coding: HEVC
    def match_video_coding(content: str, start: int, end: int) -> tuple[str, int, int]:
        match, left, right = NameParser.match_field("video_coding", content)
        if match != None:
            # Todo: convert to standard format
            video_coding = match[0]
            end = min(end, left)
            return video_coding, start, end
        logger.info(f"Parse name {content} failed, can not find video coding")
        return None, start, end
    
    # format: MP4
    def match_format(content: str, start: int, end: int) -> tuple[str, int, int]:
        match, left, right = NameParser.match_field("video_format", content)
        if match != None:
            format = match[0]
            end = min(end, left)
            return format, start, end
        
        match, left, right = NameParser.match_field("subtitle_format", content)
        if match != None:
            format = match[0]
            end = min(end, left)
            return format, start, end
        
        logger.info(f"Parse name {content} failed, can not find format")
        return None, start, end
    
    # source: (WebRip)|(Baha)
    def match_source(content: str, start: int, end: int) -> tuple[str, int, int]:
        match, left, right = NameParser.match_field("source", content)
        if match != None:
            source = match[0]
            end = min(end, left)
            return source, start, end
        
        logger.info(f"Parse name {content} failed, can not find source")
        return None, start, end
    
    def match_season(content, start, end) -> tuple[int | None, int, int]:
        match, left, right = NameParser.match_field("season", content)
        if match != None:
            season = int(match[0])
            end = min(end, left)
            return season, start, end
        
        logger.info(f"Parse name {content} failed, can not find season")
        return 1, start, end
    
    def match_subtitle_language(content, start, end) -> tuple[str, int, int]:
        match, left, right = NameParser.match_field("subtitle_language", content)
        if match != None:
            subtitle_language = match[0]
            end = min(end, left)
            return subtitle_language, start, end
        
        logger.info(f"Parse name {content} failed, can not find subtitle_language")
        return None, start, end
    
    def match_subtitle_hardcoded(content, start, end) -> tuple[str, int, int]:
        match, left, right = NameParser.match_field("subtitle_hardcoded", content)
        if match != None:
            subtitle_hardcoded = True if match[0] in ["内嵌"] else False
            end = min(end, left)
            return subtitle_hardcoded, start, end
        
        logger.info(f"Parse name {content} failed, can not find subtitle_hardcoded")
        return None, start, end
    
    def match_special(content, start, end) -> tuple[str | None, int, int]:
        match, left, right = NameParser.match_field("special", content)
        if match != None:
            special = match[0]
            end = min(end, left)
            return special, start, end
        
        logger.info(f"Parse name {content} failed, can not find special")
        return None, start, end

    # title
    def match_title(content: str, start: int, end: int) -> list[str]:
        pattern: str
        for pattern in GlobalManager.global_config.pattern_title_exclude_front:
            match = re.search(pattern, content)
            if match:
                start = max(start, match.end())
        while start <= end and NameParser.is_exclude_char(content[start]):
            start = start + 1

        for pattern in GlobalManager.global_config.pattern_title_exclude_back:
            match = re.search(pattern, content)
            if match:
                end = min(end, match.start())
        while start <= end and NameParser.is_exclude_char(content[end - 1]):
            end = end - 1
        # Todo: fix title start with or end with ()[]{}
        titles = content[start:end].split("/")
        for index, title in enumerate(titles):
            titles[index] = title.strip()
            titles[index] = NameParser.fix_brackets(title)
        return titles

    def parse(content: str):
        start = 0
        end = len(content)

        info = {}
        info["provider"], start, end = NameParser.match_provider(content, start, end)
        info["index"], start, end = NameParser.match_index(content, start, end)
        info["resolution"], start, end = NameParser.match_resolution(content, start, end)
        info["audio_coding"], start, end = NameParser.match_audio_coding(content, start, end)
        info["video_coding"], start, end = NameParser.match_video_coding(content, start, end)
        info["format"], start, end = NameParser.match_format(content, start, end)
        info["source"], start, end = NameParser.match_source(content, start, end)
        info["season"], start, end = NameParser.match_season(content, start, end)
        info["subtitle_language"], start, end = NameParser.match_subtitle_language(content, start, end)
        info["subtitle_hardcoded"], start, end = NameParser.match_subtitle_hardcoded(content, start, end)
        info["special"], start, end = NameParser.match_special(content, start, end)

        info["titles"] = NameParser.match_title(content, start, end)
        return info

if __name__ == "__main__":
    examples = [
        #r'''[Up to 21°C] 在地下城寻求邂逅是否搞错了什么 第五季 / Dungeon ni Deai wo Motomeru no wa Machigatteiru Darou ka V - 11 (CR 1920x1080 AVC AAC MKV)''',
        #r'''[Up to 21°C] 鸭乃桥论的禁忌推理 / Kamonohashi Ron no Kindan Suiri 2nd Season - 25 (Baha 1920x1080 AVC AAC MP4)[383.17 MB]''',
        #r'''[桜都字幕组] 在地下城寻求邂逅是否搞错了什么 第五季 / Dungeon ni Deai o Motomeru no wa Machigatte Iru Darouka： Familia Myth V [11][1080p][简繁内封]''',
        #r'''【喵萌奶茶屋】★10月新番★[Chi。-关于地球的运动- / Chi. Chikyuu no Undou ni Tsuite][12][1080p][繁日双语][招募翻译]''',
        #r'''[喵萌奶茶屋&LoliHouse] 物语系列 / Monogatari Series: Off & Monster Season - 02 抚物语 [WebRip 1080p HEVC-10bit AAC ASSx2][简繁日内封字幕]''',
        #r'''[LoliHouse] S级怪兽《贝希摩斯》被误认成小猫，成为精灵女孩的骑士（宠物）一起生活 / Beheneko - 01 [WebRip 1080p HEVC-10bit AAC][简繁内封字幕]''',
        #r'''[Up to 21°C] 最狂辅助职业【话术士】世界最强战团听我号令 / Saikyou no Shienshoku 'Wajutsushi' - 12 (ABEMA 1920x1080 AVC AAC MP4)''',
        #r'''[S1百综字幕组] GIRLS BAND CRY [13][WebRip][x265_EAC3][简繁内封][v2]''',
        #r'[北宇治字幕组] GIRLS BAND CRY [01-13 修正合集][WebRip][HEVC_AAC][简体内嵌]',
        #r'[7³ACG&❀拨雪寻春❀] 不时用俄语小声说真心话的邻桌艾莉同学/Tokidoki Bosotto Russia Go S01 | 01-12 [简繁字幕] BDrip 1080p x265 FLAC 2.0',
        #r'[DBD-Raws][不时轻声地以俄语遮羞的邻座艾莉同学/Tokidoki Bosotto Rossiya-go de Dereru Tonari no Alya-san/时々ボソッとロシア语でデレる隣のアーリャさん][01-08TV][BOX1-2][1080P][BDRip][HEVC-10bit][FLAC][MKV]',
        r'[桜都字幕组] 86 -不存在的战区- / 86—Eitishikkusu— [18.5][720p@60FPS][简体内嵌]',
        r'[天月搬运组] 无意间变成狗，被喜欢的女生捡回家。 / Inu ni Nattara Suki na Hito ni Hirowareta. - 14(OVA2) [1080P][简繁日外挂]',
    ]
    parser = NameParser()
    for example in examples:
        parser.parse(example)
    