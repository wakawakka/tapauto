import asyncio
import json
import logging
import signal
import zlib
import random

import utils
import notpixel_tools
from centrifuge_mod import (
    CentrifugeError,
    Client,
    ClientEventHandler,
    ConnectedContext,
    ConnectingContext,
    DisconnectedContext,
    ErrorContext,
    ServerJoinContext,
    ServerLeaveContext,
    ServerPublicationContext,
    ServerSubscribedContext,
    ServerSubscribingContext,
    ServerUnsubscribedContext,
)
import settings
from exceptions import *

TIMEOUT = 90


class ClientEventLoggerHandler(ClientEventHandler):
    """Check out comments of ClientEventHandler methods to see when they are called."""

    def __init__(
        self, event_data: asyncio.Queue, initial_image_container: asyncio.Queue, logger
    ):
        super().__init__()
        self.event_data = event_data
        self.initial_image = initial_image_container
        self.logger = logger

    async def on_connecting(self, ctx: ConnectingContext) -> None:
        self.logger.info("connecting: %s", ctx)

    async def on_connected(self, ctx: ConnectedContext) -> None:
        if ctx.data:
            await self.initial_image.put(ctx.data)
        # self.logger.info("connected: %s", ctx)
        self.logger.info(
            "connect to server-side: has data:  %s",
            ctx.data is not None,
        )
        pass

    async def on_disconnected(self, ctx: DisconnectedContext) -> None:
        self.logger.info("disconnected: %s", ctx)

    async def on_error(self, ctx: ErrorContext) -> None:
        self.logger.error("client error: %s", ctx)

    async def on_subscribed(self, ctx: ServerSubscribedContext) -> None:
        self.logger.info("subscribed server-side sub: %s", ctx)

    async def on_subscribing(self, ctx: ServerSubscribingContext) -> None:
        self.logger.info("subscribing server-side sub: %s", ctx)

    async def on_unsubscribed(self, ctx: ServerUnsubscribedContext) -> None:
        self.logger.info("unsubscribed from server-side sub: %s", ctx)

    async def on_publication(self, ctx: ServerPublicationContext) -> None:
        # self.logger.info(
        #     "publication from server-side: channel: %s, data:  %s",
        #     ctx.channel,
        #     ctx.pub.data[:40],
        # )
        if ctx.channel == "pixel:message":
            decompressed_data = zlib.decompress(ctx.pub.data, wbits=-15)
            jdata = json.loads(decompressed_data)
            await self.event_data.put(jdata)

    async def on_join(self, ctx: ServerJoinContext) -> None:
        self.logger.info("join in server-side sub: %s", ctx)

    async def on_leave(self, ctx: ServerLeaveContext) -> None:
        self.logger.info("leave in server-side sub: %s", ctx)


class Fucka:
    def __init__(
        self,
        proxy_host=None,
        proxy_port=None,
        proxy_user=None,
        proxy_password=None,
        logfile_path="common.log",
        logging_level=logging.DEBUG,
        logging_name="Centrifucka unnamed",
    ):
        self.client = None

        self.proxy_host = proxy_host
        self.proxy_port = int(proxy_port) if proxy_port is not None else 0
        self.proxy_user = proxy_user
        self.proxy_password = proxy_password

        self.buffer = asyncio.Queue()
        self.initial_image_buffer = asyncio.Queue()
        self.logger = utils.get_logger(
            filepath=logfile_path, level=logging_level, name=logging_name
        )

    async def init_client(self, token: str, user_agent: str):
        self.logger.debug(f"Starting CENTRIFURE with {token}")
        self.client = Client(
            "wss://notpx.app/connection/websocket",
            events=ClientEventLoggerHandler(
                event_data=self.buffer,
                initial_image_container=self.initial_image_buffer,
                logger=self.logger,
            ),
            # token=token,
            use_protobuf=True,
            name="js",
            headers={
                "User-Agent": user_agent,
            },
            data=json.dumps({"token": token}).encode(),
            proxy_host=self.proxy_host,
            proxy_port=self.proxy_port,
            proxy_user=self.proxy_user,
            proxy_password=self.proxy_password,
        )
        return True

    async def emulate_centrifuga_connect(self):
        await self.client.connect()
        await self.client.disconnect()
        self.logger.info("Success emulation centrifuga connecting.")

    async def collect(self):
        await self.client.connect()
        while self.buffer.qsize() < 5:
            print(self.buffer.qsize())

            await asyncio.sleep(0.5)
        await self.client.disconnect()

    async def paint_pixel(self, pixel_id, color):
        if not color.startswith("#"):
            color = f"#{color}"
        data = {"type": 0, "pixelId": pixel_id, "color": color}
        data_enc = json.dumps(data).encode()
        r = await self.client.rpc("rеpаintTournаment", data=data_enc)
        return r.data

    async def collect_pixels_and_repaint(self, count: int, good_pixels: dict):
        balance_data = []
        painted = 0
        try:
            async with asyncio.timeout(TIMEOUT):
                await self.client.connect()
                repaint_pixels = {}
                while len(repaint_pixels) < count:
                    if not self.initial_image_buffer.empty():
                        initial_image = await self.initial_image_buffer.get()
                        current_template_state_pixels = (
                            await notpixel_tools.load_template_state_from_world(
                                initial_image
                            )
                        )
                        random_pixel_order = list(current_template_state_pixels.keys())
                        random.shuffle(random_pixel_order)

                        for pixel_id in random_pixel_order:
                            if pixel_id in good_pixels:
                                if (
                                    current_template_state_pixels[pixel_id]
                                    != good_pixels[pixel_id]
                                ):
                                    repaint_pixels[pixel_id] = good_pixels[pixel_id]
                                    if painted < count:
                                        ret = await self.paint_pixel(
                                            pixel_id, good_pixels[pixel_id]
                                        )
                                        self.logger.info(
                                            f"Paint pixel {pixel_id} to {good_pixels[pixel_id]}, result: {ret}"
                                        )
                                        # balance_data.append(ret)
                                        painted += 1
                                    else:
                                        return
                        self.logger.info(
                            f"Got {len(repaint_pixels)} WRONG PIXELS FORM INITIAL IMAGE."
                        )
                        pass

                    elif not self.buffer.empty():
                        update = await self.buffer.get()
                        for color in update:
                            for pixel_id in update[color][::-1]:
                                if pixel_id in good_pixels:
                                    if color != good_pixels[pixel_id]:
                                        repaint_pixels[pixel_id] = good_pixels[pixel_id]
                                        if painted < count:
                                            ret = await self.paint_pixel(
                                                pixel_id, good_pixels[pixel_id]
                                            )
                                            self.logger.info(
                                                f"Paint pixel {pixel_id} to {good_pixels[pixel_id]}, result: {ret}"
                                            )
                                            # balance_data.append(ret)
                                            painted += 1
                                        else:
                                            return
                        self.logger.info(
                            f"Got {len(repaint_pixels)} WRONG PIXELS FORM UPDATE."
                        )
                        pass
                    await asyncio.sleep(0.2)
                await self.client.disconnect()
                self.logger.info(f"Got REPAINT pixels {repaint_pixels}")
                return repaint_pixels
        except BaseException as e:
            raise CentrifugeException(e, logger=self.logger)
        finally:
            await self.client.disconnect()


def start_fucka_debug():
    f = Fucka()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        f.init_client(
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjaGFubmVscyI6WyJldmVudDptZXNzYWdlIiwicGl4ZWw6bWVzc2FnZSJdLCJleHAiOjE3MzQ4Mzg1NjEsInN1YiI6IjcyNjU1MTU2MCJ9.-g_JLB0Jb1iQPqeK0sAGZW_h2L6uq8LNq1fyR9jDFmQ",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0",
        )
    )
    loop.create_task(f.client.connect())
    loop.run_forever()


def collect_pixels():
    f = Fucka()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        f.init_client(
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjaGFubmVscyI6WyJldmVudDptZXNzYWdlIiwicGl4ZWw6bWVzc2FnZSJdLCJleHAiOjE3MzQ4Mzg3NDcsInN1YiI6IjcyNjU1MTU2MCJ9.5Jcm8G2k28xlyWEXVI1toHl07AmZ4mzRik62SvI9sbE",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0",
        )
    )
    # loop.run_until_complete(f.collect())
    x = 128
    y = 0
    size = 64
    good_pixels = {1024 * y + i + 1: "3690EA" for i in range(x, x + size)}
    pixels_to_repaint = loop.run_until_complete(
        f.collect_pixels_and_repaint(
            count=3,
            good_pixels=good_pixels,
        )
    )
    print(pixels_to_repaint)
    pass


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    # Configure centrifuge-python logger.
    cf_logger = logging.getLogger("centrifuge")
    cf_logger.setLevel(logging.INFO)
    # start_fucka_debug()
    collect_pixels()
