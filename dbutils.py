import logging
import asyncio

import aiosqlite

import utils
import settings

init_table_queries = [
    """CREATE TABLE "user" (
	"id"	INTEGER NOT NULL UNIQUE,
    "number"    TEXT UNIQUE,
    "tdata_path"    TEXT UNIQUE,
    "password"  TEXT,
    "proxy" TEXT,
    "status" TEXT,
    "balance" INGEGER,
    "good_runs" INTEGER NOT NULL DEFAULT 0,
    "bad_runs" INTEGER NOT NULL DEFAULT 0,
    "disabled" INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY("id" AUTOINCREMENT)
);""",
]


class TDB:
    def __init__(
        self, dbpath, logfile_path="common.log", logging_level=logging.DEBUG, name="db"
    ):
        self.logger = utils.get_logger(
            filepath=logfile_path, level=logging_level, name=name
        )
        self.db_path = dbpath
        self.con = None

    async def init_db(self):
        self.con = await aiosqlite.connect(self.db_path)
        self.logger.debug(f"Connection open: {self.db_path}")

    async def get_tables(self):
        query = "SELECT name FROM sqlite_schema WHERE type ='table' AND name NOT LIKE 'sqlite_%';"
        async with await self.con.execute(query) as cursor:
            data = await cursor.fetchall()
            tables = [i[0] for i in data]
            self.logger.debug(f"Got table list: {tables}")
        return tables

    async def drop_tables(self):
        tables = await self.get_tables()
        for table_name in tables:
            query = f"DROP TABLE IF EXISTS {table_name};"
            async with await self.con.execute(query) as cursor:
                self.logger.debug(f"DROP table '{table_name}' success")
                await self.con.commit()

    async def init_schema(self):
        for q in init_table_queries:
            async with await self.con.execute(q) as cursor:
                await self.con.commit()
        self.logger.debug(f"Create schema success")

    async def add_user(self, number, tdata_path, password=None, proxy=None):
        query = (
            "insert into user (number, tdata_path, password, proxy) values (?,?,?, ?)"
        )
        try:
            async with await self.con.execute(
                query,
                (
                    number,
                    tdata_path,
                    password,
                    proxy,
                ),
            ) as cursor:
                await self.con.commit()
            self.logger.debug(f"User INSERT {number} success")
        except BaseException as e:
            self.logger.error(f"User INSERT {number} fail. reason: {e}")

    async def get_users(self):
        query = (
            "select number, tdata_path, password, proxy from user where disabled = 0"
        )
        async with await self.con.execute(
            query,
        ) as cursor:
            rows = await cursor.fetchall()
        self.logger.debug(f"Got {len(rows)} users enabled users from database")
        users = [
            {
                "number": i[0],
                "tdata_path": i[1],
                "telegram_password": i[2],
                "proxy": i[3],
            }
            for i in rows
        ]
        return users

    async def set_user_status(self, number, status):
        query = "update user set status = ? where number = ?"
        async with await self.con.execute(query, (status, number)) as cursor:
            await self.con.commit()

    async def set_user_balance(self, number, balance):
        query = "update user set balance = ? where number = ?"
        async with await self.con.execute(query, (balance, number)) as cursor:
            await self.con.commit()

    async def log_run_attempt(self, number, success):
        if success:
            query = "update user set good_runs = good_runs + 1 where number = ?"
        else:
            query = "update user set bad_runs = bad_runs + 1 where number = ?"
        async with await self.con.execute(query, (number,)) as cursor:
            await self.con.commit()

    async def close_db(self):
        if self.con:
            await self.con.close()


async def init_database():
    db = TDB(settings.db_path)
    await db.init_db()
    drop_old = input("Drop old data? y/n: ")
    if drop_old == "y":
        await db.drop_tables()
    await db.init_schema()
    await db.close_db()


if __name__ == "__main__":
    asyncio.run(init_database())
