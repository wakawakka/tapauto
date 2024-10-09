import requests
import code
import asyncio
from PIL import Image
import io
import logging
from uuid import uuid4


def get_logger(filepath=None, level=logging.INFO) -> logging.Logger:
    logger_id = uuid4().hex[:4]
    logger = logging.Logger(logger_id)
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        # "%(asctime)s - %(levelname)s - %(message)s"
    )

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if filepath:
        fh = logging.FileHandler(filepath, encoding="utf8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


def rgb_to_hex(pix):
    r, g, b = pix
    r, g, b = int(r), int(g), int(b)
    # return hex((r << 16) + (g << 8) + b).replace('0x','#').upper()
    n = (r << 16) + (g << 8) + b
    return f"#{n:06X}"


def parse_proxy_url(proxy_url):
    import re
    from urllib.parse import urlparse

    parsed_url = urlparse(proxy_url)

    # Extracting proxy host and port
    proxy_host = parsed_url.hostname
    proxy_port = parsed_url.port

    # Extracting proxy username and password from userinfo
    if parsed_url.username and parsed_url.password:
        proxy_user = parsed_url.username
        proxy_pass = parsed_url.password
    else:
        proxy_user = None
        proxy_pass = None
    return proxy_host, proxy_port, proxy_user, proxy_pass


def get_image_state(proxies=None):
    image_url = "https://image.notpx.app/api/v2/image"
    r = requests.get(image_url, proxies=proxies)
    if r.status_code == 200:
        img_io = io.BytesIO(r.content)
        img_io.seek(0)
    else:
        print(
            f"Fail to get image state (get request). Status: {r.status_code}, Error: {r.text}"
        )
        return False
    img = Image.open(img_io)
    return img


async def get_job(img, location):
    img_pixels = img.load()
    init_x = location[0]
    init_y = location[1]

    world_picture = get_image_state(proxies=None)
    world_picture_pixels = world_picture.load()
    pixels_to_paint = []

    for x_pad in range(img.size[0]):
        for y_pad in range(img.size[1]):

            x, y = init_x + x_pad, init_y + y_pad
            # code.interact(local=locals())
            # print(x, y, img_pixels[x_pad, y_pad], world_picture_pixels[x, y])
            if img_pixels[x_pad, y_pad] == world_picture_pixels[x, y]:
                print(f"Same same {x}:{y}")
            else:
                print(
                    f"Need paint {x}:{y}. Ours: {img_pixels[x_pad, y_pad]}, Theirs: f{world_picture_pixels[x, y]}"
                )
                pixels_to_paint.append((x, y, img_pixels[x_pad, y_pad]))

    return pixels_to_paint
