import asyncio
import logging
import signal
import zlib
import json

from centrifuge_mod import (
    CentrifugeError,
    Client,
    ClientEventHandler,
    ConnectedContext,
    ConnectingContext,
    DisconnectedContext,
    ErrorContext,
    ServerSubscribedContext,
    ServerSubscribingContext,
    ServerUnsubscribedContext,
    ServerPublicationContext,
    ServerJoinContext,
    ServerLeaveContext,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
# Configure centrifuge-python logger.
cf_logger = logging.getLogger("centrifuge")
cf_logger.setLevel(logging.INFO)


class ClientEventLoggerHandler(ClientEventHandler):
    """Check out comments of ClientEventHandler methods to see when they are called."""

    def __init__(self, event_data: list, papa):
        super().__init__()
        self.event_data = event_data
        self.papa = papa

    async def on_connecting(self, ctx: ConnectingContext) -> None:
        logging.info("connecting: %s", ctx)

    async def on_connected(self, ctx: ConnectedContext) -> None:
        logging.info("connected: %s", ctx)

    async def on_disconnected(self, ctx: DisconnectedContext) -> None:
        logging.info("disconnected: %s", ctx)

    async def on_error(self, ctx: ErrorContext) -> None:
        logging.error("client error: %s", ctx)

    async def on_subscribed(self, ctx: ServerSubscribedContext) -> None:
        logging.info("subscribed server-side sub: %s", ctx)

    async def on_subscribing(self, ctx: ServerSubscribingContext) -> None:
        logging.info("subscribing server-side sub: %s", ctx)

    async def on_unsubscribed(self, ctx: ServerUnsubscribedContext) -> None:
        logging.info("unsubscribed from server-side sub: %s", ctx)

    async def on_publication(self, ctx: ServerPublicationContext) -> None:
        logging.info("publication from server-side sub: %s", ctx.pub.data[:40])
        if ctx.channel == "pixel:message":
            decompressed_data = zlib.decompress(ctx.pub.data, wbits=-15)
            jdata = json.loads(decompressed_data)
            self.event_data.append(jdata)

    async def on_join(self, ctx: ServerJoinContext) -> None:
        logging.info("join in server-side sub: %s", ctx)

    async def on_leave(self, ctx: ServerLeaveContext) -> None:
        logging.info("leave in server-side sub: %s", ctx)


class Fucka:
    def __init__(self):
        self.client = None
        self.reconnect_lock = asyncio.Lock()
        self.buffer = []

    async def init_client(self):
        # async with self.reconnect_lock:
        self.client = Client(
            "wss://notpx.app/connection/websocket",
            events=ClientEventLoggerHandler(event_data=self.buffer, papa=self),
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjaGFubmVscyI6WyJldmVudDptZXNzYWdlIiwicGl4ZWw6bWVzc2FnZSJdLCJleHAiOjE3Mjk3MDIxNTMsInN1YiI6IjcyNjU1MTU2MCJ9.vxKT7hvGp_pO20z8u2TOgyDf0O1IlcMCAobTBpx_joo",
            use_protobuf=True,
            name="js",
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0",
            },
            proxy_host="f.proxys5.net",
            proxy_port=6200,
            proxy_user="07196708-zone-custom-region-CA-sessid-C9xbLErb-sessTime-120",
            proxy_password="6pGOVG0G",
        )
        return True

    async def collect(self):
        await self.client.connect()
        while len(self.buffer) < 5:
            print(len(self.buffer))
            await asyncio.sleep(0.5)
        await self.client.disconnect()


def collect_pixels():
    f = Fucka()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(f.init_client())
    loop.run_until_complete(f.collect())

    pass


if __name__ == "__main__":
    collect_pixels()


exit()
