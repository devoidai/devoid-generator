# Devoid Generator
**Official python client [Devoid Client](https://github.com/devoidai/devoid-client).**

`FastAPI`
`MongoDB`
`Using s3 bucket storage`
`Fully asynchronous`
`Works with websockets`
`Priority requests feature`
`Average generation time`
`Requests Balancer`
`Works with Kandinsky and Automatic1111`

## Setup

Devoid Generator requires [python 3.10.6](https://www.python.org/downloads/release/python-3106/) to run.

**Install the dependencies:**

```sh
cd devoid-generator
pip install -r requirements.txt
```

**Configure .env file:**
```python
TEST_MODE = 1

LOGGING_LEVEL=INFO

SAVE_IMAGES_LOCALLY=0
IMAGES_PATH=gens/

MONGODB_URI=
MONGODB_DB=

S3_ENDPOINT=
S3_ACCESS_KEY=
S3_SECRET_KEY=
S3_BUCKET_NAME=
S3_IMAGE_ENDPOINT=

SERVICES=telegram:service_key discord:service_key web:service_key

API_HOST=0.0.0.0 
API_PORT=80

GENERAL_PREMIUM_RATIO=1 3

KANDINSKY_API_TOKEN=
```
Run:

```sh
python src/main.py
```

If everything is done correctly, the server will be launched at http://localhost:80.


## Documentation

After the run, the documentation will be available at http://localhost:80/docs.

### Enums
```python
Service:
    TELEGRAM = "telegram"
    DISCORD = "discord"
    TEST = "test"
    
MessageType:
    REQUEST = "request"
    RESPONSE = "response"
    INFO = "info"
    
GenType:
    TEXT2IMG = "text2img"
    IMG2IMG = "img2img"
    MIX2IMG = "mix2img"
    
GenStatus:
    OK = "ok"
    ERROR = "error"
    QUEUED = "queued"
    GENERATING = "generating"
    
ContentType:
    TEXT = "text"
    BASE64 = "base64"
    IMAGE_URL = "image_url"

ExecutorType:
    KANDINSKY = "kandinsky"
    AUTOMATIC1111 = "automatic1111"
```

### Websockets
Websocket endpoint: `ws://localhost:80/ws`. It is used to queue a request and return the results of generation.


## Websocket Messaging

Devoid Generator works as a *request balancer*. It does not change (only validates) payload for [Automatic1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui) and [Devoid Kandinsky Api](https://github.com/devoidai/kandinsky_api). So for a detailed description of the **payload** parameter, refer to the official documentation of the listed apis.

### Client -> Devoid Generator
**Generation request**
```python
{
    "message_type": MessageType,
    "executor": ExecutorType,
    "gen_type": GenType,
    "settings": {
        "premium": 1,
        "moderate": 1,
        "sync_with_s3": 1
    },
    "service_info": {
        "user_id": 123,
        "chat_id": 123,     # Optional
        "message_id": 123   # Optional
    },
    "payload": PAYLOAD
}
```

### Devoid Generator -> Client
**Request Queued or Generating**
```python
{
    "object_id": id,
    "service": Service,
    "message_type": MessageType,
    "executor": ExecutorType,
    "gen_type": GenType,
    "gen_status": GenStatus,
    "avg_time": 0.0,
    "service_info": {
        "user_id": 123,
        "chat_id": 123,     # Optional
        "message_id": 123   # Optional
    }
}
```

**Request Done**
```python
{
    "object_id": id,
    "service": Service,
    "message_type": MessageType,
    "executor": ExecutorType,
    "gen_type": GenType,
    "gen_status": GenStatus,
    "avg_time": 0.0,
    "result": {
        "content_type": ContentType,
        "content": 0,
        "file_name": ''
    },
    "settings": {
        "premium": 1,
        "moderate": 1,
        "sync_with_s3": 1
    },
    "service_info": {
        "user_id": 123,
        "chat_id": 123,     # Optional
        "message_id": 123   # Optional
    },
    "payload": PAYLOAD
}
```

**Request Error**
```python
{
    "object_id": id,
    "service": Service,
    "message_type": MessageType,
    "executor": ExecutorType,
    "gen_type": GenType,
    "gen_status": GenStatus,
    "avg_time": 0.0,
    "result": {
        "content_type": ContentType,
        "content": 0
    },
    "settings": {
        "premium": 1,
        "moderate": 1,
        "sync_with_s3": 1
    },
    "service_info": {
        "user_id": 123,
        "chat_id": 123,     # Optional
        "message_id": 123   # Optional
    },
    "payload": PAYLOAD
}
```
