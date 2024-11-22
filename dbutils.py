import logging
import asyncio
import datetime

import aiosqlite

import utils
import settings

init_table_queries = [
    """CREATE TABLE "notpixel" (
	"id"	INTEGER NOT NULL UNIQUE,
	"number"	TEXT UNIQUE,
	"disabled"	INTEGER NOT NULL DEFAULT 0,
	"status"	TEXT,
	"balance"	INGEGER,
	"good_runs"	INTEGER NOT NULL DEFAULT 0,
	"bad_runs"	INTEGER NOT NULL DEFAULT 0,
	"start_param"	TEXT,
	"start_param_run_count"	INTEGER DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT)
);""",
    """CREATE TABLE "notpixel_secret_tries" (
	"number"	TEXT,
	"word"	TEXT,
	"responce"	TEXT
);""",
    """CREATE TABLE "telegram_user" (
	"id"	INTEGER NOT NULL UNIQUE,
	"number"	TEXT UNIQUE,
	"telegram_user_id"	INTEGER,
	"tag"	TEXT,
	"status"	TEXT,
	"tdata_path"	TEXT UNIQUE,
	"password"	TEXT,
	"proxy"	TEXT,
	"disabled"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT)
)""",
]


class TDB:
    def __init__(
        self,
        dbpath,
        logfile_path="common.log",
        logging_level=logging.DEBUG,
        logger_name="db",
    ):
        self.logger = utils.get_logger(
            filepath=logfile_path, level=logging_level, name=logger_name
        )
        self.db_path = dbpath

    async def get_tables(self):
        async with aiosqlite.connect(self.db_path) as con:
            query = "SELECT name FROM sqlite_schema WHERE type ='table' AND name NOT LIKE 'sqlite_%';"
            async with await con.execute(query) as cursor:
                data = await cursor.fetchall()
                tables = [i[0] for i in data]
                self.logger.debug(f"Got table list: {tables}")
            return tables

    async def drop_tables(self):
        tables = await self.get_tables()
        async with aiosqlite.connect(self.db_path) as con:
            for table_name in tables:
                query = f"DROP TABLE IF EXISTS {table_name};"
                async with await con.execute(query) as cursor:
                    self.logger.debug(f"DROP table '{table_name}' success")
                    await con.commit()

    async def init_schema(self):
        for q in init_table_queries:
            async with aiosqlite.connect(self.db_path) as con:
                async with await con.execute(q) as cursor:
                    await con.commit()
        self.logger.debug(f"Create schema success")

    async def add_telegram_user(self, number, tdata_path, password=None, proxy=None):
        async with aiosqlite.connect(self.db_path) as con:
            query = "insert into telegram_user (number, tdata_path, password, proxy) values (?,?,?,?)"
            try:
                async with await con.execute(
                    query,
                    (number, tdata_path, password, proxy),
                ) as cursor:
                    await con.commit()
                self.logger.debug(f"User INSERT {number} success")
            except BaseException as e:
                self.logger.error(f"User INSERT {number} fail. reason: {e}")

    async def get_telegram_users(self, tag):
        async with aiosqlite.connect(self.db_path) as con:
            query = "select number, tdata_path, password, proxy from telegram_user where disabled = 0 and tag = ?"
            async with await con.execute(query, (tag,)) as cursor:
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

    async def set_telegram_user_password(self, number, password):
        async with aiosqlite.connect(self.db_path) as con:
            query = "update telegram_user set password = ? where number = ?"
            async with await con.execute(query, (password, number)) as cursor:
                await con.commit()

    async def set_telegram_user_status(self, number, status):
        query = "update telegram_user set status = ? where number = ?"
        async with aiosqlite.connect(self.db_path) as con:
            async with await con.execute(query, (status, number)) as cursor:
                await con.commit()

    async def set_telegram_user_id(self, number, telegram_user_id):
        query = "update telegram_user set telegram_user_id = ? where number = ?"
        async with aiosqlite.connect(self.db_path) as con:
            async with await con.execute(query, (telegram_user_id, number)) as cursor:
                await con.commit()

    # NOTPIXEL METHODS

    async def is_user_pixel_task_enabled(self, number):
        query = "select id from notpixel where number = ?"
        async with aiosqlite.connect(self.db_path) as con:
            async with await con.execute(query, (number,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return True

    async def set_notpixel_user_status(self, number, status):
        query = "update notpixel set status = ? where number = ?"
        async with aiosqlite.connect(self.db_path) as con:
            async with await con.execute(query, (status, number)) as cursor:
                await con.commit()

    async def set_notpixel_user_balance(self, number, balance):
        async with aiosqlite.connect(self.db_path) as con:
            query = "update notpixel set balance = ? where number = ?"
            async with await con.execute(query, (balance, number)) as cursor:
                await con.commit()

    async def log_notpixel_run_attempt(self, number, success):
        if success:
            query = "update notpixel set good_runs = good_runs + 1 where number = ?"
        else:
            query = "update notpixel set bad_runs = bad_runs + 1 where number = ?"
        async with aiosqlite.connect(self.db_path) as con:
            async with await con.execute(query, (number,)) as cursor:
                await con.commit()

    async def add_notpixel_start_param_run(self, number):
        query = "update notpixel set start_param_run_count = start_param_run_count + 1 where number = ?"
        async with aiosqlite.connect(self.db_path) as con:
            async with await con.execute(query, (number,)) as cursor:
                await con.commit()

    async def get_notpixel_start_param(self, number):
        async with aiosqlite.connect(self.db_path) as con:
            query = "select start_param, start_param_run_count from notpixel where number = ?"
            async with await con.execute(query, (number,)) as cursor:
                row = await cursor.fetchone()
                start_param = row[0]
                start_param_run_count = row[1]
        if start_param and start_param_run_count < 5:
            return start_param

    async def add_notpixel_secret_try(self, number: str, word: str, responce: str):
        async with aiosqlite.connect(self.db_path) as con:
            query = "insert into notpixel_secret_tries (number, word, responce) values (?, ?, ?)"
            async with await con.execute(query, (number, word, responce)) as cursor:
                await con.commit()

    async def get_notpixel_secret_tries(self, number) -> set:
        async with aiosqlite.connect(self.db_path) as con:
            query = "select word from notpixel_secret_tries where number = ?"
            async with await con.execute(query, (number,)) as cursor:
                word_rows = await cursor.fetchall()
                words = [i[0] for i in word_rows]
                return set(words)


async def init_database():
    db = TDB(settings.db_path)
    # db = TDB("test.db")
    drop_old = input("Drop old data? y/n: ")
    if drop_old == "y":
        await db.drop_tables()
    await db.init_schema()


if __name__ == "__main__":
    asyncio.run(init_database())
