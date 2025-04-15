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
            logger.debug(e, stack_info = True, exc_info = True)
        self.rules = rules
        self.remain = self.rules["remain"]

    def _get_nested_attr(self, obj, attr_path):
        """
        根据 "a.b.c" 的路径，递归获取嵌套属性或字典键值
        支持混合对象属性和字典属性
        """
        for attr in attr_path.split('.'):
            try:
                # 先尝试用对象属性方式访问
                obj = getattr(obj, attr)
            except AttributeError:
                try:
                    # 如果失败，则尝试用字典键方式访问
                    obj = obj[attr]
                except (KeyError, TypeError):
                    return null
        return obj

    def _check(self, rule: dict, item: Any) -> bool:
        if rule["operator"] == "equal":
            return self._get_nested_attr(item, rule["field"]) == rule["value"]
        if rule["operator"] == "has":
            attr = self._get_nested_attr(item, rule["field"])
            if attr == None:
                return False
            return rule["value"] in attr
        if rule["operator"] == "not":
            return not self._check(rule["value"], item)
        if rule["operator"] == "and":
            return self._check(rule["value"][0], item) and self._check(rule["value"][1], item) 
        if rule["operator"] == "or":
            return self._check(rule["value"][0], item) or self._check(rule["value"][1], item) 

    def filter(self, inputs: list[Any]) -> list[tuple[int, Any]]:
        output = [(index, item) for index, item in enumerate(inputs)]
        try:
            for rule in self.rules["rules"]:
                logger.debug(f"filter {rule} apply to {len(output)} inputs")
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
                        for index, item in output:
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
