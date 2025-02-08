import logging
logger = logging.getLogger(__name__)

from typing import Any
import json

from manager.global_manager import GlobalManager

class Fliter:
    def __init__(self, rules = None):
        try: 
            if not rules:
                rules = GlobalManager.global_config.default_fliter_rule
            if type(rules) == str:
                rules = json.loads(rules)
        except Exception as e:
            logger.error(f"Cannot parse rules {rules}, please check the format")
        self.rules = rules
        self.remain = self.rules["remain"]

    def _check(self, rule: dict, item: Any) -> bool:
        if rule["operator"] == "equal":
            if type(item) == dict:
                return item[rule["field"]] == rule["value"]
            else:
                return getattr(item, rule["field"]) == rule["value"]
        if rule["operator"] == "has":
            if type(item) == dict:
                if item[rule["field"]] == None:
                    return False
                return rule["value"] in item[rule["field"]]
            else:
                if getattr(item, rule["field"]) == None:
                    return False
                return rule["value"] in getattr(item, rule["field"])
        if rule["operator"] == "not":
            return not self._check(rule["value"], item)
        if rule["operator"] == "and":
            return self._check(rule["value"][0], item) and self._check(rule["value"][1], item) 
        if rule["operator"] == "or":
            return self._check(rule["value"][0], item) or self._check(rule["value"][1], item) 

    def filter(self, input: list[Any]) -> list[tuple[int, Any]]:
        output = [(index, item) for index, item in enumerate(input)]
        try:
            for rule in self.rules["rules"]:
                match rule["type"]:
                    case "include":
                        temp = []
                        for index, item in output:
                            if self._check(rule, item):
                                temp.append((index, item))
                        if len(temp) >= self.remain:
                            output = temp
                    case "exclude":
                        temp = []
                        for index, item in enumerate(input):
                            if not self._check(rule, item):
                                temp.append((index, item))
                        if len(temp) >= self.remain:
                            output = temp
                    case _:
                        logger.error(f"Fliter {rule} not implemented")
        except Exception as e:
            logger.error(f"Cannot parse rules {self.rules}, please check the format")
            logger.debug(e, stack_info = True, exc_info = True) 

        return output[:self.remain]