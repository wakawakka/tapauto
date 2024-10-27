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
upgrade_charge_count = {2: 5, 3: 100, 4: 200, 5: 300, 6: 400, 7: None}

sessions_dir = "sessions_dir"
db_path = "tgdb.db"
log_dir = "logs"

from settings_local import *

os.makedirs(sessions_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)
