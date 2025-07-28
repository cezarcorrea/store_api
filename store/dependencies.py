from psycopg_pool import AsyncConnectionPool
from store.db.db_postgres import db_client


async def get_db_pool() -> AsyncConnectionPool:
    """Fornece o pool de conexão assíncrono do banco de dados."""
    if db_client.pool is None or db_client.pool.closed:
        raise RuntimeError("Database pool is not initialized or is closed.")
    return db_client.pool
