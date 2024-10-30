from dbutils import *

import os

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

    for num in os.listdir(path):
        acc_path = os.path.join(path, num)
        tdata_path = os.path.join(acc_path, r'tdata')
        password = None
        if "Twofa.txt" in os.listdir(acc_path):
            password = open(os.path.join(acc_path, "Twofa.txt")).read()
        assert 'proxy.txt' in os.listdir(acc_path)
        with open(os.path.join(acc_path, 'proxy.txt')) as f:
            cntnt = f.read()
        proxy = cntnt.split('\n')[0]
        #if not 
        await db.add_user(num, tdata_path, password=password, proxy=proxy, startparam="f212725752")

def make_proxies(path, proxies_path):
    with open(proxies_path) as f:
        proxies = f.read().split('\n')
    i = 0
    step=10
    for num in os.listdir(path):
        acc_path = os.path.join(path, num)
        with open(os.path.join(acc_path, 'proxy.txt'),'w') as f:
            f.write('\n'.join(proxies[i:i+step]))
            i+=step

if __name__ == "__main__":
    path = r"C:\Users\gburgerfuck\Desktop\NOTPIXEL_RUNS\RUN_2710\data"
    proxies_path = r"C:\Users\gburgerfuck\Desktop\NOTPIXEL_RUNS\RUN_2710\proxies.txt"
    make_proxies(path, proxies_path)
    db = TDB(settings.db_path)

    asyncio.run(init_database(path))