import asyncio
import io
import logging

import aiohttp
import requests
from aiohttp_socks import ChainProxyConnector, ProxyConnector, ProxyType
from PIL import Image

from exceptions import BadStatus, HttpTimeout, HttpError
from utils import get_logger


async def http_request(
    rtype,  # GET|POST
    url,
    headers,
    proxy=None,
    data_p=None,
    json_p=None,
    http_timeout=30,
    good_statuses=[200],
    logger=None,
    retry_count=3,
    read_only_part_bytes=None,
):
    if not logger:
        logger = get_logger("common.log", logging.DEBUG)
    proxy_connector = None
    if proxy:
        proxy_connector = ProxyConnector.from_url(proxy)
    try:
        async with asyncio.timeout(http_timeout):
            async with aiohttp.ClientSession(connector=proxy_connector) as session:
                match rtype:
                    case "GET":
                        roperator = session.get
                    case "POST":
                        roperator = session.post
                    case "PUT":
                        roperator = session.put
                    case "OPTIONS":
                        roperator = session.options
                    case _:
                        raise Exception(
                            f"BAD request type '{rtype}'. Allowed: GET,POST,PUT,OPTIONS"
                        )
                while retry_count:
                    try:
                        async with roperator(
                            url, headers=headers, json=json_p, data=data_p
                        ) as r:
                            success = r.status in good_statuses
                            if not success:
                                raise BadStatus(
                                    proxy=proxy,
                                    url=url,
                                    status=r.status,
                                )
                            if read_only_part_bytes:
                                content = await r.content.readexactly(
                                    read_only_part_bytes
                                )
                            else:
                                content = await r.read()

                            return {"status": r.status, "content": content}
                    except BaseException as e:
                        retry_count -= 1
                        logger.error(
                            f"Failed to {rtype} {url}, left tries - {retry_count}"
                        )
                        if not retry_count:
                            raise e

    except asyncio.TimeoutError:
        raise HttpTimeout(proxy=proxy, url=url)
    except BaseException as e:
        raise HttpError(proxy=proxy, url=url, papa_Exception=e)


async def ipinfo(proxy_host, proxy_port, proxy_user, proxy_password):
    logger = get_logger("common.log", logging.DEBUG)
    headers = {"User-Agent": "curl"}
    proxy_string = f"socks5://{proxy_user}:{proxy_password}@{proxy_host}:{proxy_port}"
    result = await http_request(
        "GET",
        "https://ipinfo.io/",
        headers,
        proxy=proxy_string,
        http_timeout=10,
        good_statuses=[200],
        logger=logger,
    )
    logger.debug(result)
    status = result.get("status")
    content_len = len(result.get("content"))
    logger.info(
        f"Finish GET info URL GET, status: {status}, content len: {content_len}"
    )


def rgb_to_hex(pix):
    r, g, b = pix
    r, g, b = int(r), int(g), int(b)
    # return hex((r << 16) + (g << 8) + b).replace('0x','#').upper()
    n = (r << 16) + (g << 8) + b
    return f"{n:06X}"


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


def get_pixels(image_file_content):
    img_io = io.BytesIO(image_file_content)
    img_io.seek(0)
    img = Image.open(img_io)
    pixels = img.load()
    return pixels


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
