from pydantic import BaseModel
from typing import Type

def convert(item, model_type: Type[BaseModel]) -> BaseModel:
    model_data = {}
    for field_name, field_type in model_type.__annotations__.items():
        if hasattr(item, field_name):
            model_data[field_name] = getattr(item, field_name)
    return model_type(**model_data)