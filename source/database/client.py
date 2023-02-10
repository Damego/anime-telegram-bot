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
            CREATE TABLE IF NOT EXISTS subscriptions(
                user_id varchar(255) NOT NULL,
                title_type varchar(10) NOT NULL,
                code varchar(255) NOT NULL
            )
            """
        )
        await self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chapters(
                title_type varchar(255) NOT NULL,
                code varchar(255) NOT NULL,
                chapter varchar(255) NOT NULL
            )
            """
        )

    async def subscribe(self, title_type: str, user_id: int, code: str):
        await self.connection.execute(f"INSERT INTO subscriptions VALUES ($1, $2, $3)", str(user_id), title_type, code)

    async def unsubscribe(self, title_type: str, user_id: int, code: str):
        await self.connection.execute(
            f"DELETE FROM subscriptions WHERE user_id=$1 AND title_type=$2 AND code=$3", str(user_id), title_type, code
        )

    async def get_users_from_code(self, title_type: str, code: str) -> list[asyncpg.Record]:
        return await self.connection.fetch(
            f"SELECT user_id FROM subscriptions WHERE title_type=$1, code=$12", title_type, code
        )

    async def get_title_codes(self, title_type: str) -> list[asyncpg.Record]:
        return await self.connection.fetch(
            f"SELECT DISTINCT code FROM subscriptions WHERE title_type=$1", title_type
        )

    async def get_subscription_entry(self, title_type: str, user_id: int, code: str) -> list[asyncpg.Record]:
        return await self.connection.fetch(
            f"SELECT * from subscriptions WHERE user_id=$1 AND title_type=$2 AND code=$3", str(user_id), title_type, code
        )