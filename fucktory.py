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
import pandas as pd

from notpixel_actions import PixelActions
import notpixel_tools
import settings
import telegram_utils
import secure_browser
import notpixel_tools
import notpixel_actions


class Worker:
    def __init__(self, tg_acc_name):
        self.tg_acc_name = tg_acc_name


class Fucktory:
    def __init__(self, picture_path, location):
        self.img = Image.open(picture_path).convert("RGB")
        self.pixels = self.img.load()
        assert len(location) == 2  # x, y
        assert type(location[0]) == int
        assert type(location[1]) == int
        self.location = location
        print(f"Initialized Fucktory size of {self.img.size}")
        # code.interact(local=locals())

    def get_job(self):
        self.task = notpixel_tools.get_job(self.img, self.location)

    def get_workers(self, fname):
        self.workers_fname = fname
        with open(fname) as f:
            self.workers = json.load(f)

    def dump_workers(self):
        with open(self.workers_fname, "w") as f:
            f.write(json.dumps(self.workers, indent=4))

    def split_task_by_workers(self, task):
        pass

    def single_run(self, worker, task):
        proxy_host, proxy_port, proxy_user, proxy_password = (
            notpixel_tools.parse_proxy_url("https://" + worker["proxy"])
        )
        tg = telegram_utils.Telega(
            session_id=worker["number"],
            telegram_cache_dir=settings.telegram_cache,
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            proxy_user=proxy_user,
            proxy_password=proxy_password,
        )
        tdata_path = worker["path"]
        account_password = worker.get('password', None)
        tg.init_client_tdata(
            tdata_path, platform="desktop", hardware_id="228", password=account_password
        )
        app_url = tg.get_bot_webapp(
            bot_username="notpixel",
            url="https://notpx.app",
            platform="android",
        )
        huy_v_rot_styles = "&tgWebAppThemeParams=%7B%22accent_text_color%22%3A%22%23168acd%22%2C%22bg_color%22%3A%22%23ffffff%22%2C%22bottom_bar_bg_color%22%3A%22%23ffffff%22%2C%22button_color%22%3A%22%2340a7e3%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22destructive_text_color%22%3A%22%23d14e4e%22%2C%22header_bg_color%22%3A%22%23ffffff%22%2C%22hint_color%22%3A%22%23999999%22%2C%22link_color%22%3A%22%23168acd%22%2C%22secondary_bg_color%22%3A%22%23f1f1f1%22%2C%22section_bg_color%22%3A%22%23ffffff%22%2C%22section_header_text_color%22%3A%22%23168acd%22%2C%22section_separator_color%22%3A%22%23e7e7e7%22%2C%22subtitle_text_color%22%3A%22%23999999%22%2C%22text_color%22%3A%22%23000000%22%7D"
        print(app_url + huy_v_rot_styles)
        pa = notpixel_actions.PixelActions(
            app_url + huy_v_rot_styles,
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            proxy_user=proxy_user,
            proxy_password=proxy_password,
            gui_browser_worker_type=False,
            headless=True,
        )
        job_result = pa.run(task)
        if pa.sb:
            pa.sb.browser.close()
        return job_result

    def run_sequentially(self, catch=True):
        for worker_name, worker in self.workers.items():
            print("NA RABOTU SUKA:", worker)
            failed = False
            if catch:
                try:
                    result = self.single_run(worker, self.task)
                except Exception as e:
                    print(f"ERROR for {worker}, {e}, {str(e)}")
                    result = {}
                    worker["last_status"] = f"{e}"
                    failed = True
            else:
                result = self.single_run(worker, self.task)

            painted = result.get("painted", [])
            charges = result.get("charges", 0)
            charges_full_restore_time = result.get(
                "charges_full_restore_time", "UNKNOWN"
            )

            worker["last_run"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            worker["full_restore_time"] = charges_full_restore_time
            if not failed:
                worker["last_status"] = f"painted {len(painted)}, left {charges}"
            self.workers[worker_name] = worker

            self.dump_workers()

            for i, point in enumerate(painted):
                assert self.task[i][0] == point[0]
                assert self.task[i][1] == point[1]
            self.task = self.task[len(painted) :]
            if len(self.task) == 0:
                print("ALL PAINTED!!!!!!")
                break
        else:
            print(f"All worker used, but still left {len(self.task)} points(")


if __name__ == "__main__":
    picture_path = "./notpixel_settings/228.png"
    slaves_path = "slaves.json"
    fk = Fucktory(picture_path, (228, 228))
    fk.get_job()
    # code.interact(local=locals())
    # some logic on how much workers needed for task
    fk.get_workers(slaves_path)
    # some logic on parallel/non parallel run of the job
    fk.run_sequentially(catch=False)
    code.interact(local=locals())
