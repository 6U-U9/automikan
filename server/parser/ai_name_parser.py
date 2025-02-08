import logging
logger = logging.getLogger(__name__)
import json
from openai import OpenAI, DefaultHttpxClient

from parser import Parser
from manager.global_manager import GlobalManager
from utils.string import list_to_string

class AiNameParser(Parser):
    def parse(content: str):
        if GlobalManager.global_config.ai_proxy_url != None:
            client = OpenAI(
                api_key = GlobalManager.global_config.ai_api_key,
                base_url = GlobalManager.global_config.ai_base_url,
                http_client = DefaultHttpxClient(
                    proxy = GlobalManager.global_config.ai_proxy_url
                ),
            )
        else:
            client = OpenAI(
                api_key = GlobalManager.global_config.ai_api_key,
                base_url = GlobalManager.global_config.ai_base_url,
            )

        completion = client.chat.completions.create(
            model = GlobalManager.global_config.ai_model, 
            messages = [
                {"role": "system", "content": GlobalManager.global_config.ai_prompt},
                {"role": "user", "content": content},
            ],
        )

        reply = json.loads(completion)

        info = {}
        info["provider"] = list_to_string(reply.get("provider", None))
        info["index"] = reply.get("index", [0, 0])
        info["resolution"] = list_to_string(reply.get("resolution", None))
        info["audio_coding"] = list_to_string(reply.get("audio_coding", None))
        info["video_coding"] = list_to_string(reply.get("video_coding", None))
        info["format"] = list_to_string(reply.get("format", None))
        info["source"] = list_to_string(reply.get("source", None))
        info["season"] = reply.get("season", 1)
        info["subtitle_language"] = list_to_string(reply.get("subtitle_language", None))
        info["subtitle_hardcoded"] = reply.get("subtitle_hardcoded", None)
        info["special"] = list_to_string(reply.get("special", None))
        info["titles"] = reply.get("titles", [])
        return info