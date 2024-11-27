import asyncio
import logging
import os
import random
import datetime
import time

import dbutils
import secure_browser
import notpixel_actions
import tapswap_actions
import settings
import utils
from notpixel_tools import parse_proxy_url
from telegram_utils import Telega

NOTPIXEL_BOT_USERNAME = "notpx_bot"
TAPSWAP_BOT_USERNAME = "tapswap_mirror_1_bot"

TELEGRAM_PLATFORM = "desktop"
WEBAPP_PLATFORM = "android"

RESTART_TIMEOUT = 20 * 60  # 20 minutes
SINGLE_RUN_TIMEOUT = 5 * 60
SUCCESS_JOB_DONE_MAX_ADD_SLEEP_TILE = 15 * 60
SIMPLIFIED_SLEEP = 60 * 60 * 8 + 228

WORKER_INITIAL_START_TIMEOUT = 15


class LOCAL_JS_EMULATOR:
    browser = None


class Worker:

    def __init__(
        self,
        tdata_path: str,
        telegram_session_id: int,
        db: dbutils.TDB,
        start_datetime: datetime.datetime,
        proxy_host: str = None,
        proxy_port: int = None,
        proxy_user: str = None,
        proxy_password: str = None,
        telegram_password: str = None,
    ):
        self.tdata_path = tdata_path
        self.worker_start_datetime = start_datetime
        self.telegram_session_id = telegram_session_id

        self.log_filename = os.path.join(
            settings.log_dir, f"{self.telegram_session_id}.log"
        )

        self.logger = utils.get_logger(
            filepath=self.log_filename,
            level=logging.DEBUG,
            name=f"worker:{telegram_session_id}",
        )

        self.db = db

        self.telegram_password = telegram_password

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
            telegram_user_data = await self.tg.init_client_tdata(
                tdata_path=self.tdata_path,
                platform=platform,
                hardware_id=self.telegram_session_id,
                password=self.telegram_password,
                raise_current_session_run=False,
            )

            telegram_user_id = telegram_user_data.get("telegram_user_id", None)
            if telegram_user_id:
                await self.db.set_telegram_user_id(
                    self.telegram_session_id, str(telegram_user_id)
                )

            new_password = await self.tg.check_password()

            if new_password:
                await self.db.set_telegram_user_password(
                    self.telegram_session_id, new_password
                )

            return {"success": True, "id": self.telegram_session_id, "exception": None}
        except BaseException as e:
            return {"success": False, "id": self.telegram_session_id, "exception": e}

    async def complete_telegram_task(self, task):
        task_id = task.get("id")
        task_type = task.get("type")
        task_target = task.get("target")
        task_data = task.get("data")

        match task_type:
            case "subscribe":
                subscribe_success = await self.tg.subscribe_channel(channel=task_target)
                if subscribe_success:
                    self.logger.info(
                        f"Subscribe telegram task completed. Target: {task_target}"
                    )
                    await self.db.set_telegram_task_done(task_id)
            case _:
                self.logger.error(
                    f"Found unhandled telegram task. Type: {task_type}, Target: {task_target}, Data: {task_data}"
                )

    async def single_run_pixel(self, worker_start_datetime: datetime.datetime):
        try:
            async with asyncio.timeout(SINGLE_RUN_TIMEOUT):

                start_param = await self.db.get_notpixel_start_param(
                    self.telegram_session_id
                )
                if start_param:
                    await self.db.add_notpixel_start_param_run(self.telegram_session_id)

                user_tasks = await self.db.get_user_telegram_tasks(
                    number=self.telegram_session_id, done=0
                )
                if user_tasks:
                    await self.complete_telegram_task(task=user_tasks[0])

                # NO MORE 1 CHANNEL PER RUN
                # channel_to_subscribe = await self.db.get_channel_to_subscribe()
                # await self.subscribe_channel(channel_to_subscribe)
                # await self.db.add_user_channel_subscribe(channel_to_subscribe)

                webapp_url = await self.tg.get_bot_webapp(
                    bot_username=NOTPIXEL_BOT_USERNAME,
                    platform=WEBAPP_PLATFORM,
                    web_app_param=start_param,  # "f726551560",
                )
                pixar = notpixel_actions.PixelActions(
                    webapp_url,
                    session_id=self.telegram_session_id,
                    db=self.db,
                    worker_start_datetime=worker_start_datetime,
                    proxy_host=self.proxy_host,
                    proxy_port=self.proxy_port,
                    proxy_user=self.proxy_user,
                    proxy_password=self.proxy_password,
                    logfile_path=self.log_filename.replace(".log", ".pixel.log"),
                    logging_level=logging.DEBUG,
                    logging_name=f"px:{self.telegram_session_id}",
                )
                account_state = await pixar.repaint_pixels()
                balance = account_state.get("balance")
                await self.db.set_notpixel_user_balance(
                    number=self.telegram_session_id, balance=int(balance)
                )
                await self.db.log_notpixel_run_attempt(
                    number=self.telegram_session_id, success=True
                )
                await self.db.set_notpixel_user_status(
                    number=self.telegram_session_id, status="GOOD"
                )

                if not settings.SIMPLIFIED:
                    full_restore_timeout = (
                        account_state.get("max_charges") - account_state.get("charges")
                    ) * account_state.get("charge_restore_speed")

                    random_sleep_size = random.randint(
                        0, SUCCESS_JOB_DONE_MAX_ADD_SLEEP_TILE
                    )

                    sleeptime = full_restore_timeout + random_sleep_size
                else:
                    sleeptime = SIMPLIFIED_SLEEP
                return sleeptime

        except BaseException as e:
            await self.db.log_notpixel_run_attempt(
                number=self.telegram_session_id, success=False
            )
            await self.db.set_notpixel_user_status(
                number=self.telegram_session_id, status=str(e)
            )
            self.logger.error(
                f"Worker {self.telegram_session_id} breaks with: {e}",
                stack_info=True,
            )
            return RESTART_TIMEOUT

    async def single_run_tapswap(
        self, worker_start_datetime: datetime.datetime, selenium_js_emu_browser
    ):
        try:
            async with asyncio.timeout(SINGLE_RUN_TIMEOUT):

                bot_start_param = await self.db.get_tapswap_bot_start_param(
                    number=self.telegram_session_id
                )
                if not bot_start_param:
                    bot_start_param = "start"

                user_tasks = await self.db.get_user_telegram_tasks(
                    number=self.telegram_session_id, done=0
                )
                if user_tasks:
                    await self.complete_telegram_task(task=user_tasks[0])
                # here

                webapp_url = await self.tg.get_bot_webapp_noapp(
                    bot_username=TAPSWAP_BOT_USERNAME,
                    platform=WEBAPP_PLATFORM,
                    bot_start_param=bot_start_param,
                )

                telegram_user_id = await self.db.get_telegram_user_id(
                    number=self.telegram_session_id
                )
                self.logger.info(f"Telegram user id: {telegram_user_id}")
                if not telegram_user_id:
                    raise Exception(
                        f"Telegram user id for {self.telegram_session_id} not set"
                    )

                tapswaper = tapswap_actions.TapswapActions(
                    web_app_entry_url=webapp_url,
                    db=self.db,
                    telegram_session_id=self.telegram_session_id,
                    telegram_user_id=telegram_user_id,
                    selen=selenium_js_emu_browser,
                    worker_start_datetime=worker_start_datetime,
                    proxy_host=self.proxy_host,
                    proxy_port=self.proxy_port,
                    proxy_user=self.proxy_user,
                    proxy_password=self.proxy_password,
                    logfile_path=self.log_filename.replace(".log", ".tapswap.log"),
                    logging_level=logging.DEBUG,
                    logging_name=f"tap:{self.telegram_session_id}",
                )

                await tapswaper.make_actions()

                await self.db.log_tapswap_run_attempt(
                    number=self.telegram_session_id, success=True
                )
                await self.db.set_tapswap_user_status(
                    number=self.telegram_session_id, status="GOOD"
                )

                if not settings.SIMPLIFIED:
                    dt_now = datetime.datetime.now()  # TODO NIGHT MODE
                    sleeptime = 60 * 60 * random.randint(1, 2)
                else:
                    sleeptime = SIMPLIFIED_SLEEP
                return sleeptime

        except BaseException as e:
            await self.db.log_tapswap_run_attempt(
                number=self.telegram_session_id, success=False
            )
            await self.db.set_tapswap_user_status(
                number=self.telegram_session_id, status=str(e)
            )
            self.logger.error(
                f"Worker {self.telegram_session_id} breaks with: {e}",
                stack_info=True,
            )
            return RESTART_TIMEOUT

    async def get_task_future(self, task_type):
        if task_type in settings.EXECUTION_BAN_TASKS:
            self.logger.error(f"TASK {task_type} BANNED FOR EXECUTION.")
            return
        match task_type:
            case settings.PIXEL_TASK_NAME:
                return self.single_run_pixel(self.worker_start_datetime)
            case settings.TAPSWAP_TASK_NAME:
                if not LOCAL_JS_EMULATOR.browser:
                    self.logger.error(
                        "Local JS emulator browser is required to TapSwap bot farm"
                    )
                return self.single_run_tapswap(
                    self.worker_start_datetime, LOCAL_JS_EMULATOR.browser
                )
            case _:
                self.logger.error(f"BAD TASK TYPE: {task_type}")

    async def create_initial_raspisanie(self):
        raspisanie = {}

        # NOTPIXEL TASK
        user_pixel_task_enabled = await self.db.is_user_pixel_task_enabled(
            self.telegram_session_id
        )
        if user_pixel_task_enabled:
            self.logger.info(f"Pixel task ENABLED for {self.telegram_session_id}")
            raspisanie[time.time()] = settings.PIXEL_TASK_NAME
            await asyncio.sleep(0.5)

        # TAPSWAP TASK
        user_tapswap_task_enabled = await self.db.is_user_tapswap_task_enabled(
            number=self.telegram_session_id
        )
        if user_tapswap_task_enabled:
            self.logger.info(f"TapSwap task ENABLED for {self.telegram_session_id}")
            raspisanie[time.time()] = settings.TAPSWAP_TASK_NAME
            await asyncio.sleep(0.5)

        if not raspisanie:
            self.logger.error(f"WORKER: {self.telegram_session_id} RASPISANIE EMPTY")
        return raspisanie

    async def poyti_na_smenu(self):

        raspisanie = await self.create_initial_raspisanie()
        if not raspisanie:
            return

        while True:  # ebashit bez vukhodnux

            current_ts = time.time()
            task_key = None
            for start_ts in raspisanie:
                if current_ts > start_ts:
                    task_key = start_ts
                    break
            if task_key:
                task_type = raspisanie.pop(task_key)
                task_future = await self.get_task_future(task_type)
                if not task_future:
                    continue
                timeout = await task_future
                next_start_ts = time.time() + timeout
                next_start_dt_s = datetime.datetime.fromtimestamp(
                    next_start_ts
                ).isoformat()
                self.logger.info(
                    f"Worker {self.telegram_session_id} plan {task_type} to {next_start_dt_s}. GO SLEEP FOR {timeout} sec"
                )
                raspisanie[next_start_ts] = task_type
            await asyncio.sleep(1)


async def get_workers(db: dbutils.TDB):

    enabled_workers_data = await db.get_telegram_users(tag=settings.TAG)
    workers = {}
    for user in enabled_workers_data:
        number = user.get("number")
        proxy = user.get("proxy")
        proxy_host, proxy_port, proxy_user, proxy_password = parse_proxy_url(
            "https://" + proxy
        )

        worker_start_time = datetime.datetime.now(datetime.UTC)

        workers[number] = Worker(
            tdata_path=user.get("tdata_path"),
            telegram_session_id=number,
            db=db,
            start_datetime=worker_start_time,
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

    workers = await get_workers(db)
    init_client_tasks = []
    _i = 0
    for worker_id in workers:
        init_client_tasks.append(
            asyncio.create_task(
                workers[worker_id].init_telegram_client(platform=TELEGRAM_PLATFORM)
            )
        )
        _i += 1
        if _i % 50 == 0:
            await asyncio.sleep(10)

    unloaded_workers = set()
    for client_init in asyncio.as_completed(init_client_tasks):
        result = await client_init

        success = result.get("success")
        worker_id = result.get("id")

        if success:
            logger.info(f"Success init telegram session {worker_id}")
            await db.set_telegram_user_status(number=worker_id, status="LOADED")
        else:
            unloaded_workers.add(worker_id)
            exception = result.get("exception")
            logger.error(f"Failed init telegram session {worker_id}. {exception}")
            await db.set_telegram_user_status(number=worker_id, status=str(exception))
            workers.pop(worker_id)

    logger.info("CLIENT LOADING SUMMARY")
    logger.info("\tGOOD:")
    for worker_id in workers:
        logger.info(f"\t\t{worker_id}")
    logger.info("\tBAD:")
    for worker_id in unloaded_workers:
        logger.info(f"\t\t{worker_id}")
    input("Press enter to start BIG WORK on GOOD workers")

    logger.info("Starting local js browser emulator")
    LOCAL_JS_EMULATOR.browser = secure_browser.SecChromeBrowser(headless=True)

    for worker_id in workers:
        logger.info(f"STARTING SMENA OF WORKER: {worker_id}")
        loop.create_task(workers[worker_id].poyti_na_smenu())
        await asyncio.sleep(WORKER_INITIAL_START_TIMEOUT)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.create_task(run_fucktory())
    loop.run_forever()
