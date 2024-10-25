import logging

import aiosqlite

import utils

init_table_queries = [
    """CREATE TABLE "proxy" (
	"id"	INTEGER NOT NULL UNIQUE,
	"country"	TEXT,
	"city"	TEXT,
	"host"	TEXT,
    "port"  INTEGER,
    "user"  TEXT,
    "password"  TEXT,
    "quality"   TEXT,
    "quality_last_check"    TEXT,
	"lock"	INTEGER NOT NULL DEFAULT 0,
 	UNIQUE("host","port","user","password"),
	PRIMARY KEY("id" AUTOINCREMENT)
);""",
    """CREATE TABLE "user" (
	"id"	INTEGER NOT NULL UNIQUE,
    "number"    TEXT,
    "tdata_path"    TEXT,
    "password"  TEXT,
    "status" TEXT,
    "proxy_id" INTEGER,
    PRIMARY KEY("id" AUTOINCREMENT)
);""",
    """CREATE TABLE "pixel" (
    "id"	INTEGER NOT NULL UNIQUE,
    "user_id"   INTEGER,
    "charges"   INTEGER,
    "max_charges"   INTEGER,
    "charge_restore" INTEGER,
    "template_id" INTEGER,
    PRIMARY KEY("id" AUTOINCREMENT)
);
""",
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

    async def add_proxy(
        self,
        proxy_host,
        proxy_port,
        proxy_user,
        proxy_password,
        country=None,
        city=None,
    ):
        query = (
            "insert into proxy (country, city, host, port, user, password) "
            "values ?,?,?,?,?"
        )
        async with await self.con.execute(query) as cursor:
            await self.con.commit()
        self.logger.debug(
            f"Proxy INSERT {country}, {city} {proxy_user}:{proxy_password}@{proxy_host}:{proxy_port}"
        )

    async def close_db(self):
        if self.con:
            await self.con.close()
