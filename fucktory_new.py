import asyncio
import logging
import os

import dbutils
import notpixel_actions
import settings
import utils
from notpixel_tools import parse_proxy_url
from telegram_utils import Telega

BOT_USERNAME = "notpx_bot"
TELEGRAM_PLATFORM = "desktop"
WEBAPP_PLATFORM = "android"

EXCEPTION_START_TIMEOUT = 10 * 60  # 10 minutes


class Worker:

    def __init__(
        self,
        tdata_path: str,
        telegram_session_id: int,
        db: dbutils.TDB,
        proxy_host: str = None,
        proxy_port: int = None,
        proxy_user: str = None,
        proxy_password: str = None,
        telegram_password: str = None,
    ):
        self.tdata_path = tdata_path
        self.telegram_password = telegram_password
        self.telegram_session_id = telegram_session_id

        self.log_filename = os.path.join(
            settings.log_dir, f"{self.telegram_session_id}.log"
        )

        self.db = db

        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_user = proxy_user
        self.proxy_password = proxy_password

        self.tg = None

    async def init_telegram_client(self, platform="desktop"):
        try:
            self.tg = Telega(
                telegram_cache_dir=settings.sessions_dir,
                session_id=self.telegram_session_id,
                proxy_host=self.proxy_host,
                proxy_port=self.proxy_port,
                proxy_user=self.proxy_user,
                proxy_password=self.proxy_password,
                logfile_path=self.log_filename,
                logging_level=logging.DEBUG,
                logging_name=f"tg:{self.telegram_session_id}",
            )
            await self.tg.init_client_tdata(
                tdata_path=self.tdata_path,
                platform=platform,
                hardware_id=self.telegram_session_id,
                password=self.telegram_password,
            )
            return {"success": True, "id": self.telegram_session_id, "exception": None}
        except BaseException as e:
            return {"success": False, "id": self.telegram_session_id, "exception": e}

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
                logging_name=f"px:{self.telegram_session_id}",
            )
            account_state = await pixar.repaint_pixels()

            full_restore_timeout = (
                account_state.get("max_charges") - account_state.get("charges")
            ) * account_state.get("charge_restore_speed")
            balance = account_state.get("balance")

            await self.db.set_user_balance(
                number=self.telegram_session_id, balance=int(balance)
            )
            await self.db.log_run_attempt(number=self.telegram_session_id, success=True)

            return full_restore_timeout
        except BaseException as e:
            await self.db.log_run_attempt(
                number=self.telegram_session_id, success=False
            )
            await self.db.set_user_status(
                number=self.telegram_session_id, status=str(e)
            )
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


async def get_workers(db: dbutils.TDB):

    enabled_workers_data = await db.get_users()
    workers = {}
    for user in enabled_workers_data:
        number = user.get("number")
        proxy = user.get("proxy")
        proxy_host, proxy_port, proxy_user, proxy_password = parse_proxy_url(
            "https://" + proxy
        )

        workers[number] = Worker(
            tdata_path=user.get("tdata_path"),
            telegram_session_id=number,
            db=db,
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            proxy_user=proxy_user,
            proxy_password=proxy_password,
            telegram_password=user.get("telegram_password"),
        )
    return workers


async def run_fucktory():
    loop = asyncio.get_event_loop()

    fucktory_logfile = "fucktory.log"

    logger = utils.get_logger(fucktory_logfile, level=logging.DEBUG, name="FUCK")

    db = dbutils.TDB(settings.db_path, logfile_path=fucktory_logfile)
    await db.init_db()

    workers = await get_workers(db)
    init_client_tasks = [
        asyncio.create_task(
            workers[worker_id].init_telegram_client(platform=TELEGRAM_PLATFORM)
        )
        for worker_id in workers
    ]
    unloaded_workers = set()
    for client_init in asyncio.as_completed(init_client_tasks):
        result = await client_init

        success = result.get("success")
        worker_id = result.get("id")

        if success:
            logger.info(f"Success init telegram session {worker_id}")
        else:
            unloaded_workers.add(worker_id)
            exception = result.get("exception")
            await db.set_user_status(number=worker_id, status=str(exception))
            workers.pop(worker_id)
    logger.info("CLIENT LOADING SUMMARY")
    logger.info("\tGOOD:")
    for worker_id in workers:
        logger.info(f"\t\t{worker_id}")
    logger.info("\tBAD:")
    for worker_id in unloaded_workers:
        logger.info(f"\t\t{worker_id}")
    input("Press enter to start BIG WORK on GOOD workers")

    for worker_id in workers:
        loop.create_task(workers[worker_id].poyti_na_smenu(logger))


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.create_task(run_fucktory())
    loop.run_forever()
