import logging
import asyncio
import datetime

import aiosqlite

import utils
import settings

init_table_queries = [
    """CREATE TABLE "user" (
	"id"	INTEGER NOT NULL UNIQUE,
	"number"	TEXT UNIQUE,
	"tdata_path"	TEXT UNIQUE,
	"password"	TEXT,
	"proxy"	TEXT,
	"status"	TEXT,
	"balance"	INGEGER,
	"good_runs"	INTEGER NOT NULL DEFAULT 0,
	"bad_runs"	INTEGER NOT NULL DEFAULT 0,
	"disabled"	INTEGER NOT NULL DEFAULT 0,
	"start_param"	TEXT,
	"start_param_run_count"	INTEGER DEFAULT 0,
	"index_page_last_update"	DATETIME,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE "secret_tries" (
	"number"	TEXT,
	"word"	TEXT,
	"responce"	TEXT
);""",
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

    async def add_user(
        self, number, tdata_path, password=None, proxy=None, startparam=None
    ):
        async with aiosqlite.connect(self.db_path) as con:
            query = "insert into user (number, tdata_path, password, proxy, start_param) values (?,?,?,?,?)"
            try:
                async with await con.execute(
                    query,
                    (number, tdata_path, password, proxy, startparam),
                ) as cursor:
                    await con.commit()
                self.logger.debug(f"User INSERT {number} success")
            except BaseException as e:
                self.logger.error(f"User INSERT {number} fail. reason: {e}")

    async def get_users(self):
        async with aiosqlite.connect(self.db_path) as con:
            query = "select number, tdata_path, password, proxy from user where disabled = 0"
            async with await con.execute(
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
        async with aiosqlite.connect(self.db_path) as con:
            query = "update user set status = ? where number = ?"
            async with await con.execute(query, (status, number)) as cursor:
                await con.commit()

    async def set_user_proxy(self, number, proxy):
        async with aiosqlite.connect(self.db_path) as con:
            query = "update user set status = ? where number = ?"
            async with await con.execute(query, (proxy, number)) as cursor:
                await con.commit()

    async def set_user_balance(self, number, balance):
        async with aiosqlite.connect(self.db_path) as con:
            query = "update user set balance = ? where number = ?"
            async with await con.execute(query, (balance, number)) as cursor:
                await con.commit()

    async def set_user_password(self, number, password):
        async with aiosqlite.connect(self.db_path) as con:
            query = "update user set password = ? where number = ?"
            async with await con.execute(query, (password, number)) as cursor:
                await con.commit()

    async def log_run_attempt(self, number, success):
        if success:
            query = "update user set good_runs = good_runs + 1 where number = ?"
        else:
            query = "update user set bad_runs = bad_runs + 1 where number = ?"
        async with aiosqlite.connect(self.db_path) as con:
            async with await con.execute(query, (number,)) as cursor:
                await con.commit()

    async def add_start_param_run(self, number):
        query = "update user set start_param_run_count = start_param_run_count + 1 where number = ?"
        async with aiosqlite.connect(self.db_path) as con:
            async with await con.execute(query, (number,)) as cursor:
                await con.commit()

    async def set_user_index_update_time(self, number, update_time: datetime.datetime):
        async with aiosqlite.connect(self.db_path) as con:
            query = "update user set index_page_last_update = ? where number = ?"
            async with await con.execute(query, (update_time, number)) as cursor:
                await con.commit()

    async def get_user_index_update_time(self, number):
        async with aiosqlite.connect(self.db_path) as con:
            query = "select index_page_last_update from user where number = ?"
            async with await con.execute(query, (number,)) as cursor:
                row = await cursor.fetchone()
                return row[0]

    # Migration
    # ALTER TABLE "user"
    # ADD start_param TEXT;

    # ALTER TABLE "user"
    # ADD start_param_run_count INTEGER DEFAULT 0;
    async def get_start_param(self, number):
        async with aiosqlite.connect(self.db_path) as con:
            query = (
                "select start_param,start_param_run_count from user where number = ?"
            )
            async with await con.execute(query, (number,)) as cursor:
                row = await cursor.fetchone()
                start_param = row[0]
                start_param_run_count = row[1]
        if start_param and start_param_run_count < 5:
            return start_param

    async def add_secret_try(self, number: str, word: str, responce: str):
        async with aiosqlite.connect(self.db_path) as con:
            query = "insert into secret_tries (number, word, responce) values (?, ?, ?)"
            async with await con.execute(query, (number, word, responce)) as cursor:
                await con.commit()

    async def get_user_old_secrets(self, number) -> set:
        async with aiosqlite.connect(self.db_path) as con:
            query = "select word from secret_tries where number = ?"
            async with await con.execute(query, (number,)) as cursor:
                word_rows = await cursor.fetchall()
                words = [i[0] for i in word_rows]
                return set(words)


async def init_database():
    db = TDB(settings.db_path)
    drop_old = input("Drop old data? y/n: ")
    if drop_old == "y":
        await db.drop_tables()
    await db.init_schema()


if __name__ == "__main__":
    asyncio.run(init_database())
