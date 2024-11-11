import os
import zipfile
import shutil
import settings
from dbutils import TDB
import asyncio


async def add_downloaded_accs_uar():

    folder = "accs_to_load"
    where = r"C:\projects\tg_accs"
    two_fa_filename = "Twofa.txt"
    proxy_file = "proxy_toronto.txt"

    db_path = settings.db_path
    db = TDB(dbpath=db_path)

    acc_arches = os.listdir(folder)
    for arch in acc_arches:
        if not ".zip" in arch:
            continue
        number = arch.replace(".zip", "")
        arch_path = os.path.join(folder, arch)
        folder_path = arch_path.replace(".zip", "")
        with zipfile.ZipFile(arch_path, "r") as z:
            z.extractall(folder_path)
            shutil.copytree(
                os.path.join(folder_path, "tdata"),
                os.path.join(where, number, "tdata"),
                dirs_exist_ok=True,
            )
            with open(os.path.join(folder_path, two_fa_filename)) as f:
                code = f.read().strip()
        with open(proxy_file) as f:
            proxy_data = f.read()
            proxies = proxy_data.strip().split("\n")
            proxy = proxies.pop(-1)
        with open(proxy_file, "w") as f:
            f.write("\n".join(proxies))
        await db.add_user(
            number=number,
            tdata_path=os.path.join(where, number, "tdata"),
            password=code,
            proxy=proxy,
            startparam="f6444194100",
        )


async def add_downloaded_accs_birma():
    folder = "accs_to_load"
    where = r"tdatas"
    proxy_file = "proxy_toronto.txt"
    code = "f959672376648"
    start_param = "f6444194100"

    db_path = settings.db_path
    db = TDB(dbpath=db_path)

    acc_arches = os.listdir(folder)
    for arch in acc_arches:
        if not ".zip" in arch:
            continue
        number = arch.replace(".zip", "").replace("+", "")
        arch_path = os.path.join(folder, arch)
        folder_path = arch_path.replace(".zip", "")
        with zipfile.ZipFile(arch_path, "r") as z:
            z.extractall(folder_path)
            shutil.copytree(
                os.path.join(folder_path, "tdata"),
                os.path.join(where, number, "tdata"),
                dirs_exist_ok=True,
            )

        with open(proxy_file) as f:
            proxy_data = f.read()
            proxies = proxy_data.strip().split("\n")
            proxy = proxies.pop(-1)
        with open(proxy_file, "w") as f:
            f.write("\n".join(proxies))
        await db.add_user(
            number=number,
            tdata_path=os.path.join(where, number, "tdata"),
            password=code,
            proxy=proxy,
            startparam=start_param,
        )


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(add_downloaded_accs_birma())
    loop.close()
    print("Finish")
