from pydantic import BaseModel
from typing import Union

class TelegramMessage(BaseModel):
    chat: Union[int, None] = None
    message: Union[int, None] = None

class DiscordMessage(BaseModel):
    guild: Union[int, None] = None
    channel: Union[int, None] = None
    message: Union[int, None] = None

class Parameters(BaseModel):
    seed: Union[int, None] = None
    steps: Union[int, None] = None
    cfg_scale: Union[int, None] = None
    width: Union[int, None] = None
    height: Union[int, None] = None

class Text2TextRequest(BaseModel):
    service: str
    service_id: int
    prompt: str
    info: Union[Parameters, None]
    discord: Union[DiscordMessage, None]
    telegram: Union[TelegramMessage, None]
    
    def __str__(self) -> str:
        return f'{self.service}:{self.service_id}'