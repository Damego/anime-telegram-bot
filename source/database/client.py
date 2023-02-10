import asyncpg


class PostgreClient:
    def __init__(self, *, host: str, port: int = 5432, user: str, password: str):
        self._host = host
        self._user = user
        self._port = port
        self._password = password

        self.connection: asyncpg.Connection = None  # type: ignore

    async def connect(self):
        self.connection = await asyncpg.connect(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            database="anime-telegram-bot-db"
        )

    async def create_tables(self):
        await self.connection.execute(
            """
            CREATE TABLE anime(
                user_id INT NOT NULL,
                code varchar(255) NOT NULL
            )
            """
        )
        await self.connection.execute(
            """
            CREATE TABLE manga(
                user_id INT NOT NULL,
                code varchar(255) NOT NULL,
                chapter varchar(50) NOT NULL
            )
            """
        )
        await self.connection.execute(
            """
            CREATE TABLE ranobe(
                user_id INT NOT NULL,
                code varchar(255) NOT NULL,
                chapter varchar(50) NOT NULL
            )
            """
        )

    async def subscribe(self, table_name: str, user_id: int, code: str):
        await self.connection.execute(f"INSERT INTO {table_name} VALUES ($1, $2)", user_id, code)

    async def unsubscribe(self, table_name: str, user_id: int, code: str):
        await self.connection.execute(
            f"DELETE FROM {table_name} WHERE user_id=$1 AND code=$2", user_id, code
        )

    async def get_users_from_code(self, table_name: str, code: str) -> list[asyncpg.Record]:
        return await self.connection.fetch(
            f"SELECT user_id FROM {table_name} WHERE code=$1", code
        )

    async def get_all_codes(self, table_name: str) -> list[asyncpg.Record]:
        return await self.connection.fetch(
            f"SELECT DISTINCT code FROM {table_name}"
        )

    async def get_row(self, table_name: str, user_id: int, code: str) -> list[asyncpg.Record]:
        return await self.connection.fetchrow(
            f"SELECT * from {table_name} WHERE user_id=$1 AND code=$2", user_id, code
        )