import io
from PIL import Image

def compress_image(image_bytes: bytes) -> bytes:
    image = Image.open(io.BytesIO(image_bytes))
    compressed_image = io.BytesIO()
    image.save(compressed_image, format='jpeg')
    return compressed_image.getvalue()