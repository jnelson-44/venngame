from psycopg_pool import AsyncConnectionPool
import os

db_pool = AsyncConnectionPool(conninfo=os.getenv("DATABASE_URL"),open=False)
