from psycopg_pool import AsyncConnectionPool

_db_pool:AsyncConnectionPool|None = None

def init(dsn:str) -> None:
    global _db_pool
    _db_pool = AsyncConnectionPool(conninfo=dsn, open=False)

def get_pool() -> AsyncConnectionPool:
    if _db_pool is None:
        raise RuntimeError("Database pool not configured; Must call Database.init(dsn:str) first")
    return _db_pool