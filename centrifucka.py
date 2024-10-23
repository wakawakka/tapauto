import asyncio
import logging
import signal
import zlib
import json

from centrifuge import (
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

    def __init__(self, state: dict, papa):
        super().__init__()
        self.state = state
        self.papa = papa

    async def on_connecting(self, ctx: ConnectingContext) -> None:
        logging.info("connecting: %s", ctx)

    async def on_connected(self, ctx: ConnectedContext) -> None:
        self.state["state"] = "CONNECTED"
        logging.info("connected: %s", ctx)

    async def on_disconnected(self, ctx: DisconnectedContext) -> None:
        self.state["state"] = "DISCONNECT"
        await self.papa.init_client()
        await self.papa.connect()
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

    async def on_join(self, ctx: ServerJoinContext) -> None:
        logging.info("join in server-side sub: %s", ctx)

    async def on_leave(self, ctx: ServerLeaveContext) -> None:
        logging.info("leave in server-side sub: %s", ctx)


class Fucka:
    def __init__(self):
        self.client = None
        self.reconnect_lock = asyncio.Lock()
        self.state = {"papa": self}

    async def init_client(self):
        # async with self.reconnect_lock:
        self.client = Client(
            "wss://notpx.app/connection/websocket",
            events=ClientEventLoggerHandler(state=self.state, papa=self),
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjaGFubmVscyI6WyJldmVudDptZXNzYWdlIiwicGl4ZWw6bWVzc2FnZSJdLCJleHAiOjE3Mjk2NzM4NDUsInN1YiI6IjcyNjU1MTU2MCJ9.YF_a2bItowdPLJb-4Kehgow9fiGORYmcVzNneNv833g",
            use_protobuf=True,
            name="js",
        )
        return True

    async def drop(self):
        while True:
            await asyncio.sleep(3)
            await self.client.disconnect()

    async def connect(self):
        await self.client.connect()

    async def printer(self):
        while True:
            print(self.state)
            await asyncio.sleep(0.5)


def run_fucka():
    f = Fucka()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(f.init_client())

    connect_task = loop.create_task(f.connect())
    drop_task = loop.create_task(f.drop())
    printer = loop.create_task(f.printer())

    loop.run_forever()

    pass


if __name__ == "__main__":
    run_fucka()


exit()
