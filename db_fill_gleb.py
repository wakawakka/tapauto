from dbutils import *

import logging
import asyncio

import aiosqlite

import utils
import settings

async def init_database(path):
    db = TDB(settings.db_path)
    drop_old = input("Drop old data? y/n: ")
    if drop_old == "y":
        await db.drop_tables()
    await db.init_schema()

    for num in path:
        acc_path = os.path.join(path, num)
        tdata_path = os.path.join(acc_path, r'tdata')
        password = None
        if "Twofa.txt" in os.listdir(acc_path):
            password = open(os.path.join(acc_path, "Twofa.txt")).read()
        assert 'proxy.txt' in os.listdir(num_path)
        with open(os.path.join(num_path, 'proxy.txt')) as f:
            cntnt = f.read()
        proxy = cntnt.split('\n')[0]
        db.add_user(number, os.path.join(path, num), password=password, proxy=proxy)


if __name__ == "__main__":
    asyncio.run(init_database())