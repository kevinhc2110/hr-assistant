from typing import Optional

import asyncpg
from pgvector.asyncpg import register_vector

from src.hr_assistant.infrastructure.database.base import Database

class PostgresDatabase(Database):

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            dsn=self.dsn
        )
        async with self.pool.acquire() as conn:
            await register_vector(conn)

    async def disconnect(self):
        await self.pool.close()

    async def execute(self, query: str, *args):
        async with self.pool.acquire() as conn:
            await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)