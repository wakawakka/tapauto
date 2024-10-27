import asyncio
import json
import logging
import signal
import zlib

import utils
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
from exceptions import *

TIMEOUT = 15


class ClientEventLoggerHandler(ClientEventHandler):
    """Check out comments of ClientEventHandler methods to see when they are called."""

    def __init__(self, event_data: asyncio.Queue, logger):
        super().__init__()
        self.event_data = event_data
        self.logger = logger

    async def on_connecting(self, ctx: ConnectingContext) -> None:
        self.logger.info("connecting: %s", ctx)

    async def on_connected(self, ctx: ConnectedContext) -> None:
        self.logger.info("connected: %s", ctx)

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
        self.logger.info("publication from server-side sub: %s", ctx.pub.data[:40])
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
        self.logger = utils.get_logger(
            filepath=logfile_path, level=logging_level, name=logging_name
        )

    async def init_client(self, token: str, user_agent: str):
        self.logger.debug(f"Starting CENTRIFURE with {token}")
        self.client = Client(
            "wss://notpx.app/connection/websocket",
            events=ClientEventLoggerHandler(event_data=self.buffer, logger=self.logger),
            token=token,
            use_protobuf=True,
            name="js",
            headers={
                "User-Agent": user_agent,
            },
            proxy_host=self.proxy_host,
            proxy_port=self.proxy_port,
            proxy_user=self.proxy_user,
            proxy_password=self.proxy_password,
        )
        return True

    async def collect(self):
        await self.client.connect()
        while self.buffer.qsize() < 5:
            print(self.buffer.qsize())

            await asyncio.sleep(0.5)
        await self.client.disconnect()

    async def collect_pixels_to_repaint(self, count: int, good_pixels: dict):
        try:
            async with asyncio.timeout(15):
                await self.client.connect()
                repaint_pixels = {}
                while len(repaint_pixels) < count:
                    if not self.buffer.empty():
                        update = await self.buffer.get()
                        for color in uspdate:
                            for pixel_id in update[color]:
                                if pixel_id in good_pixels:
                                    if color != good_pixels[pixel_id]:
                                        repaint_pixels[pixel_id] = good_pixels[pixel_id]
                                    elif pixel_id in repaint_pixels:
                                        repaint_pixels.pop(pixel_id)
                    await asyncio.sleep(0.2)
                await self.client.disconnect()
                self.logger.info(f"Got REPAINT pixels {repaint_pixels}")
                return repaint_pixels
        except BaseException as e:
            raise CentrifugeException(e, logger=self.logger)


def collect_pixels():
    f = Fucka()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        f.init_client(
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjaGFubmVscyI6WyJldmVudDptZXNzYWdlIiwicGl4ZWw6bWVzc2FnZSJdLCJleHAiOjE3Mjk4NTA0ODEsInN1YiI6IjcyNjU1MTU2MCJ9.mtck3wd2scFLEvrJxUv7twe3RZWTttkz29qsxWywXY8",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0",
        )
    )
    # loop.run_until_complete(f.collect())
    pixels_to_repaint = loop.run_until_complete(
        f.collect_pixels_to_repaint(
            count=3,
            good_pixels={
                1: "ffffff",
                2: "ffffff",
                11: "ffffff",
                22: "ffffff",
                111: "ffffff",
                222: "ffffff",
                1111: "ffffff",
                2222: "ffffff",
                11111: "ffffff",
                22222: "ffffff",
                111111: "ffffff",
                222222: "ffffff",
            },
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
    collect_pixels()
