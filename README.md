# Devoid Generator Client
**Client for [Devoid Generator](https://github.com/devoidai/devoid-generator).**

`Fully asynchronous`
`Works with websockets`
`Priority requests feature`
`Additional separate queue for each user`
`Average generation time`
## Setup

Devoid Generator Client requires [python 3.10.6](https://www.python.org/downloads/release/python-3106/) to run.

Install the dependencies:

```sh
cd devoid-client
pip install -r requirements.txt
```

## Example of usage:

### Client
Creating main client:

```python
import devoid_client 

client = GeneratorClient(
    endpoint=GENERATOR_ENDPOINT,
    service=SERVICE_NAME,
    token=SERVICE_TOKEN
)

# Running client in existing loop
loop = asyncio.get_running_loop()
client.run(loop)
```

### Handlers
**You can register 5 handlers for intermediate and final generation results:**

Import generation result representation:
```python
from devoid_client import GenerationResponse
```

**Create handlers and register it in client:**
```python
# Websocket connection error handler
async def connection_error_handler(exception: Exception):
    print(f'[{type(exception)}] {exception}')
    
client.register_con_error_handler(connection_error_handler)
```

```python
# Image Generation done handler
async def request_done_handler(response: GenerationResponse):
    request_id = response.object_id
    result = response.result.content
    user = response.service_info.user_id
    
client.register_req_done_handler(request_done_handler)
```

```python
# Image Generation error
async def request_error_handler(response: GenerationResponse):
    request_id = response.object_id
    error_text = response.result.content
    user = response.service_info.user_id
    
client.register_req_error_handler(request_error_handler)
```

```python
# Image Generation request queued
async def request_queued_handler(response: GenerationResponse):
    request_id = response.object_id
    user = response.service_info.user_id
    average_time = response.avg_time
    
client.register_req_queued_handler(request_queued_handler)
```

```python
# When image starts generating
async def request_generating_handler(response: GenerationResponse):
    request_id = response.object_id
    user = response.service_info.user_id

client.register_req_generating_handler(request_generating_handler)
```

## Image Generation
Devoid Generator works as a *request balancer*. It does not change (only validates) payload for [Automatic1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui) and [Devoid Kandinsky Api](https://github.com/devoidai/kandinsky_api). So for a detailed description of the **payload** parameter, refer to the official documentation of the listed apis.

**General parameters:**
* executor - Type of executor: Kandinsky or Automatic1111
* premium - Should be 1 for highest priority
* moderate - Prompt moderation
* sync_with_s3 - Wait for saving in s3
* user_id - Required parameter. It is necessary to identify the end user.
* chat_id - Optional
* message_id - Optional
* payload - Payload for Automatic1111 or Kandinsky
* max_user_queue_size - The maximum queue size for the user




## Kandinsky
**mix2img**
Prepare images for request:
```python
with open("example.png", "rb") as image:
    f1 = base64.b64encode(image.read())
    f1 = f1.decode('ascii')
```

Sending a request:
```python
await client1.mix2img(
    executor=Executor.KANDINSKY, 
    premium=1, 
    moderate=1, 
    sync_with_s3=True,
    user_id=2, 
    chat_id=2, 
    message_id=2, 
    payload=kandinsky_mix2img_payload,
    max_user_queue_size=1
)
```

**text2img**
Sending a request:
```python
# text2img - automatic
await client1.text2img(
    executor=Executor.KANDINSKY, 
    premium=1, 
    moderate=1, 
    sync_with_s3=True, 
    user_id=1, 
    chat_id=1, 
    message_id=1, 
    payload=kandinsky_text2img_payload, 
    max_user_queue_size=2
)
```

## Automatic1111
**img2img**
```python
await client1.img2img(
    executor=Executor.AUTOMATIC1111, 
    premium=1, 
    moderate=1, 
    sync_with_s3=True, 
    user_id=1, 
    chat_id=1, 
    message_id=1, 
    payload=automatic1111_img2img_payload, 
    max_user_queue_size=2
)
```

**text2img**
```python
# img2img - automatic
await client1.img2img(
    executor=Executor.AUTOMATIC1111, 
    premium=1, 
    moderate=1, 
    sync_with_s3=True, 
    user_id=1, 
    chat_id=1, 
    message_id=1, 
    payload=automatic1111_text2img_payload, 
    max_user_queue_size=2
)
```
