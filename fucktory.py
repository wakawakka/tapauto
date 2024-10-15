# 2 threads - potential problems with managing current situation especially when we are attacked.
# code with aim to threading in future, but without real need better not to complicate

# 1 - regulary get picture and return in [['#FFDDCC', '#FFDDAA'],] format
# 2 -
#    - load tasks from task folder
#    - ask current state of picture
#    - draw pixels (input: task, account and return coords of completed pixels)
#        - login telegram webapp during drawing (it will also auto update akk)
#        - ...
from PIL import Image
import code
import json
import time
import random
import pandas as pd
import asyncio
import aiofiles
import logging
import os

import utils
from notpixel_actions import PixelActions
import notpixel_tools
import settings
import telegram_utils
import notpixel_tools
import notpixel_actions
import utils


class Worker:
    def __init__(self, tg_acc_name):
        self.tg_acc_name = tg_acc_name


class Fucktory:

    def __init__(
        self,
        picture_path,
        location,
        logfile_path="common.log",
        logging_level=logging.DEBUG,
    ):
        self.logging_level = logging_level
        self.logger = utils.get_logger(
            filepath=logfile_path, level=logging_level, name="FuckTory"
        )

        self.img = Image.open(picture_path).convert("RGB")
        self.pixels = self.img.load()
        assert len(location) == 2  # x, y
        assert type(location[0]) == int
        assert type(location[1]) == int
        init_x = location[0]
        init_y = location[1]
        self.location = location

        self.pixellocker = {}
        for x_pad in range(self.img.size[0]):
            for y_pad in range(self.img.size[1]):
                x, y = init_x + x_pad, init_y + y_pad
                self.pixellocker[(x, y)] = asyncio.Lock()
                # залокали нахуй по идее не должно быть беды потому что обращения к pixellocker никогда не долждны ставить туда новый объект,
                # а тольео менять состояние локера, что сейф

        self.file_locker = asyncio.Lock()
        self.workers_locker = asyncio.Lock()

        self.logger.info(f"Initialized Fucktory size of {self.img.size}")
        # code.interact(local=locals())

    async def get_job(self):
        task = await notpixel_tools.get_job(self.img, self.location)
        return task

    async def initial_get_workers(self, fname):
        self.workers_fname = fname
        async with self.workers_locker:
            async with self.file_locker:
                async with aiofiles.open(fname) as f:
                    content = await f.read()
                    self.workers = json.loads(content)
                    for worker_name in self.workers:
                        self.workers[worker_name]["locker"] = asyncio.Lock()

    async def dump_workers(self):
        async with self.workers_locker:
            async with self.file_locker:
                async with aiofiles.open(self.workers_fname, "w") as f:
                    await f.write(
                        json.dumps(
                            {
                                k: {
                                    kv: vv
                                    for kv, vv in v.items()
                                    if kv not in ["locker", "tg"]
                                }
                                for k, v in self.workers.items()
                            },
                            indent=4,
                        )
                    )

    async def get_actual_workers(self):
        async with self.workers_locker:
            actual_workers = []
            for worker_name, worker in self.workers.items():
                self.logger.info(f"WORKER {worker_name}")
                # All rules to take workers write there like worker['full_restore_time'] > now etc.
                if worker["locker"].locked():
                    self.logger.info("LOCKED!!")
                    continue
                self.logger.info("FREE!")
                actual_workers.append(worker_name)
        return actual_workers

    async def estimated_charges(self, worker):
        return 5

    async def single_run(self, worker_name, tasks):
        logfile_path = os.path.join(settings.log_dir, worker_name)
        local_logger = utils.get_logger(
            filepath=logfile_path, level=self.logging_level, name=f"single_run:{worker_name}"
        )

        bot_username = "notpx_bot"
        worker = self.workers[worker_name]
        for task in tasks:
            await self.pixellocker[(task[0], task[1])].acquire()
        #job_result = {}

        try:
            async with self.workers[worker_name]["locker"]:
                proxy_host, proxy_port, proxy_user, proxy_password = (
                    notpixel_tools.parse_proxy_url("https://" + worker["proxy"])
                )
                if self.workers[worker_name].get("tg") is None:
                    local_logger.info(f"WORKER {worker_name} create NEW worker")

                    tg = telegram_utils.Telega(
                        session_id=worker["number"],
                        telegram_cache_dir=settings.telegram_cache,
                        proxy_host=proxy_host,
                        proxy_port=proxy_port,
                        proxy_user=proxy_user,
                        proxy_password=proxy_password,
                        logfile_path=logfile_path,
                        logging_level=self.logging_level,
                        name=f"tutils:{worker_name}"
                    )
                    tdata_path = worker["path"]
                    account_password = worker.get("password", None)
                    await tg.init_client_tdata(
                        tdata_path,
                        platform="desktop",
                        hardware_id=worker["number"],
                        password=account_password,
                    )

                    telegram_bot_started = worker.get("bot_started", None)
                    if not telegram_bot_started:
                        await tg.start_bot(bot_username=bot_username)
                    app_url = await tg.get_bot_webapp(
                        bot_username=bot_username,
                        url="https://notpx.app",
                        platform="android",
                    )

                    self.workers[worker_name]["tg"] = tg
                else:
                    local_logger.info(f"WORKER {worker_name} use Existing worker")
                    tg = self.workers[worker_name]["tg"]

                app_url = tg.app_url
                huy_v_rot_styles = "&tgWebAppThemeParams=%7B%22accent_text_color%22%3A%22%23168acd%22%2C%22bg_color%22%3A%22%23ffffff%22%2C%22bottom_bar_bg_color%22%3A%22%23ffffff%22%2C%22button_color%22%3A%22%2340a7e3%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22destructive_text_color%22%3A%22%23d14e4e%22%2C%22header_bg_color%22%3A%22%23ffffff%22%2C%22hint_color%22%3A%22%23999999%22%2C%22link_color%22%3A%22%23168acd%22%2C%22secondary_bg_color%22%3A%22%23f1f1f1%22%2C%22section_bg_color%22%3A%22%23ffffff%22%2C%22section_header_text_color%22%3A%22%23168acd%22%2C%22section_separator_color%22%3A%22%23e7e7e7%22%2C%22subtitle_text_color%22%3A%22%23999999%22%2C%22text_color%22%3A%22%23000000%22%7D"
                local_logger.info(app_url + huy_v_rot_styles)
                pa = notpixel_actions.PixelActions(
                    app_url + huy_v_rot_styles,
                    proxy_host=proxy_host,
                    proxy_port=proxy_port,
                    proxy_user=proxy_user,
                    proxy_password=proxy_password,
                    gui_browser_worker_type=False,
                    headless=True,
                    name=f"pa:{worker_name}",
                    logfile_path=logfile_path,
                    logging_level=self.logging_level,
                )
                local_logger.info("PA initialized")
                job_result = await pa.run(tasks)
                local_logger.info(f"task done : {job_result}")
                job_result["status"] = (
                    f"OK, painted {job_result['painted']}, left{job_result['charges']}"
                )
                if pa.sb:
                    pa.sb.browser.close()
        except asyncio.exceptions.CancelledError as e:
            local_logger.info(f"WORKER {worker_name} cancelled")
            job_result = {}
        except BaseException as e:
            local_logger.error(f"WORKER {worker_name} failed with {e}, {repr(e)}")
            try:
                self.workers[worker_name]["tg"].disconnect()
            except:
                pass
            self.workers[worker_name]["tg"] = None
            job_result = {
                "status": repr(e),
                "painted": 0,
                "charges": "UNKNOWN",
                "charges_full_restore_time": "UNKNOWN",
            }
        finally:
            for task in tasks:
                self.pixellocker[(task[0], task[1])].release()

            for j in job_result:
                worker[j] = job_result[j]
            if job_result:
                worker["last_run"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            self.workers[worker_name] = worker
            await self.dump_workers()
            return job_result

    async def run_async(self, catch=True):
        actual_job = await self.get_job()
        self.logger.info(f"CURRENT BAD POINTS {len(actual_job)}")
        actual_workers = await self.get_actual_workers()
        not_locked_actual_job = []
        for point_job in actual_job:
            if not self.pixellocker[(point_job[0], point_job[1])].locked():
                not_locked_actual_job.append(point_job)
        self.logger.info(f"CURRENT NOT LOCKED BAD POINTS {len(not_locked_actual_job)}")

        tasks = []
        offset = 0
        random.shuffle(actual_workers)
        for worker_name in actual_workers:
            charges = await self.estimated_charges(self.workers[worker_name])
            sub_job = not_locked_actual_job[offset : offset + charges]
            offset += charges
            if offset >= len(not_locked_actual_job):
                self.logger.info("ALL JOB SPLIT BY WORKERS!!!")
                break
            task = asyncio.create_task(self.single_run(worker_name, sub_job))
            tasks.append(task)
        else:
            self.logger.info(
                f"LEFT PIXELS WITOUT WORKERS: {len(not_locked_actual_job) - offset}"
            )
        self.logger.info(f"AMOUNT OF STARTED WORKERS: {len(tasks)}")
        await asyncio.gather(*tasks)

    async def do_stuff_periodically_async(self, interval, periodic_function, **kwargs):
        futures = []
        for i in range(100000):
            self.logger.info(f"Starting periodic function {i}")
            futures.append(asyncio.create_task(periodic_function(**kwargs)))
            await asyncio.sleep(interval)
            self.logger.info(f"len of runs: {len(futures)}")
            self.logger.info(
                f"len of done runs: {len([f for f in futures if f.done()])}"
            )

    def do_stuff_periodically(self, interval, periodic_function, **kwargs):
        futures = []
        loop = asyncio.new_event_loop()
        for i in range(100000):
            self.logger.info(f"Starting periodic function {i}")
            futures.append(loop.create_task(periodic_function(**kwargs)))
            time.sleep(interval)
            self.logger.info(f"len of runs: {len(futures)}")
            self.logger.info(
                f"len of done runs: {len([f for f in futures if f.done()])}"
            )


def main():
    picture_path = "./notpixel_settings/228.png"
    slaves_path = "slaves_test.json"

    fk = Fucktory(picture_path, (228, 228))
    # code.interact(local=locals())
    # some logic on how much workers needed for task
    asyncio.run(fk.initial_get_workers(slaves_path))
    # some logic on parallel/non parallel run of the job

    #asyncio.run(fk.run_async(catch=False))
    asyncio.run(fk.do_stuff_periodically_async(30, fk.run_async))


if __name__ == "__main__":
    main()
    # asyncio.run(main())
