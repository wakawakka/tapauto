import logging
import asyncio

from telegram_utils import Telega
import notpixel_actions
import utils
import settings

BOT_USERNAME = "notpx_bot"
WEBAPP_PLATFORM = "android"

EXCEPTION_START_TIMEOUT = 10 * 60  # 10 minutes


class Worker:

    def __init__(
        self,
        tdata_path: str,
        telegram_session_id: int,
        proxy_host: str = None,
        proxy_port: int = None,
        proxy_user: str = None,
        proxy_password: str = None,
        telegram_password: str = None,
    ):
        self.tdata_path = tdata_path
        self.telegram_password = telegram_password
        self.telegram_session_id = telegram_session_id

        self.log_filename = f"{self.telegram_session_id}.log"

        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_user = proxy_user
        self.proxy_password = proxy_password

        self.tg = None

    async def init_telegram_client(self, platform="windows"):
        self.tg = Telega(
            telegram_cache_dir=settings.sessions_dir,
            session_id=self.telegram_session_id,
            proxy_host=self.proxy_host,
            proxy_port=self.proxy_port,
            proxy_user=self.proxy_user,
            proxy_password=self.proxy_password,
            logfile_path=self.log_filename,
            logging_level=logging.DEBUG,
            logging_name="TELEGRAM",
        )
        await self.tg.init_client_tdata(
            tdata_path=self.tdata_path,
            platform=platform,
            hardware_id=self.telegram_session_id,
            password=self.telegram_password,
        )
        return self.telegram_session_id

    async def single_run(self, logger):
        try:
            webapp_url = await self.tg.get_bot_webapp(
                bot_username=BOT_USERNAME, platform=WEBAPP_PLATFORM
            )
            pixar = notpixel_actions.PixelActions(
                webapp_url,
                proxy_host=self.proxy_host,
                proxy_port=self.proxy_port,
                proxy_user=self.proxy_user,
                proxy_password=self.proxy_password,
                logfile_path=self.log_filename,
                logging_level=logging.DEBUG,
                logging_name="PIXEL",
            )
            account_state = await pixar.repaint_pixels()

            full_restore_timeout = (
                account_state.get("max_charges") - account_state.get("charges")
            ) * account_state.get("charge_restore_speed")
            balance = account_state.get("balance")
            # update user_balance in database
            # increase user good runs in database

            return full_restore_timeout
        except BaseException as e:
            # increase user bad runs in database
            logger.error(
                f"Worker {self.telegram_session_id} breaks with: {e}",
                stack_info=True,
            )
            return EXCEPTION_START_TIMEOUT

    async def poyti_na_smenu(self, logger):
        while True:  # ebashit bez vukhodnux
            timeout = await self.single_run(logger)
            logger.info(f"Worker {self.telegram_session_id} GO SLEEP FOR {timeout} sec")
            await asyncio.sleep(timeout)


async def get_workers():
    worker1 = Worker(
        tdata_path="tdatas/16049015240/tdata",
        telegram_session_id="16049015240",
        proxy_host="f.proxys5.net",
        proxy_port=6200,
        proxy_user="07196708-zone-custom-region-CA-city-ottawa-sessid-Qoeuiuja-sessTime-120",
        proxy_password="6pGOVG0G",
        telegram_password="Reza1357",
    )
    workers = [worker1]
    return workers


async def run_fucktory():
    loop = asyncio.get_event_loop()
    logger = utils.get_logger("fucktory.log", level=logging.DEBUG, name="FUCK")

    workers = await get_workers()

    # init all telegram clients
    init_client_tasks = [
        asyncio.create_task(worker.init_telegram_client(platform="macos"))
        for worker in workers
    ]
    for client_init in asyncio.as_completed(init_client_tasks):
        initialized_telegram_session_id = await client_init
        logger.info(f"Success init telegram session {initialized_telegram_session_id}")

    for worker in workers:
        loop.create_task(worker.poyti_na_smenu(logger))


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.create_task(run_fucktory())
    loop.run_forever()
