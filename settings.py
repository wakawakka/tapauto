import os

# upgrade to this level price
# UpgradeRepaint
upgrade_repaint_price = {2: 5, 3: 100, 4: 200, 5: 300, 6: 500, 7: 600, 8: None}
# UpgradeChargeRestoration
upgrade_charge_restoration_price = {
    2: 5,
    3: 100,
    4: 200,
    5: 300,
    6: 400,
    7: 500,
    8: 600,
    9: 700,
    10: 800,
    11: 900,
    12: None,
}
# UpgradeChargeCount
# upgrade_charge_count = {2: 5, 3: 100, 4: 200, 5: 300, 6: 400, 7: None}
upgrade_charge_count = {2: 5, 3: 100, 4: 200, 5: None}

sessions_dir = "sessions_dir"
db_path = "tgdb.db"
log_dir = "logs"
templates_dir = "templates"

free_tasks = {
    # "boinkTask": b',boinkTask:"boinkTask,"',
    "jettonTask": b'id:"jetton",reward:512,action:()=>{i("task_click"),X("https://t.me/jetton/bonus?startapp=cdQGhtRYyjY"',
    # "pumpkin": b'a=t.meta.arg.reward;i&&(s===S.pumpkin&&n.dispatch(Ci({product:7,amount:6})),n.dispatch(Lt(a)));let o="Check failed"',
}

DOWNLOAD_JS_SCRIPTS = True

from settings_local import *

os.makedirs(sessions_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)
