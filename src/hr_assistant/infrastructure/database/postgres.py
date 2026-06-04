import asyncpg

class PostgresDatabase:

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            dsn=self.dsn
        )

    async def disconnect(self):
        await self.pool.close()