from enum import Enum

class Service(Enum):
    TELEGRAM = "telegram"
    DISCORD = "discord"
    TEST = "test"
    
class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    INFO = "info"
    
class GenType(Enum):
    TEXT2IMG = "text2img"
    IMG2IMG = "img2img"
    MIX2IMG = "mix2img"
    
class GenStatus(Enum):
    OK = "ok"
    ERROR = "error"
    QUEUED = "queued"
    GENERATING = "generating"
    
class ContentType(Enum):
    TEXT = "text"
    BASE64 = "base64"
    IMAGE_URL = "image_url"

class ExecutorType(Enum):
    KANDINSKY = "kandinsky"
    AUTOMATIC1111 = "automatic1111"