from psycopg_pool import AsyncConnectionPool


class PostgresClient:
    def __init__(self):
        self.pool: AsyncConnectionPool | None = None
        self._dsn: str | None = None

    async def connect(self, dsn: str):
        if self.pool is None or self._dsn != dsn:
            if self.pool is not None and not self.pool.closed:
                await self.pool.close()
            self._dsn = dsn
            self.pool = AsyncConnectionPool(dsn, min_size=1, max_size=10, open=False)
            await self.pool.open()

            print("PostgresClient: Pool de conexão aberto.")

    async def disconnect(self):
        if self.pool and not self.pool.closed:
            await self.pool.close()
            self.pool = None
            self._dsn = None
            print("PostgresClient: Pool de conexão fechado.")

    async def get_connection(self):
        if self.pool is None or self.pool.closed:
            raise ConnectionError("Database pool is not connected or is closed.")
        return await self.pool.connection()


db_client = PostgresClient()
