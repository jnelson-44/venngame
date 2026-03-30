from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import os
from psycopg_pool import AsyncConnectionPool
import src.lib.Puzzle as Puzzle

########################################
# DATABASE & SERVER INIT               #
########################################
async def db_create_tables(pool:AsyncConnectionPool) -> None:
    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
CREATE TABLE IF NOT EXISTS solves (
  id SERIAL PRIMARY KEY,
  puzzle_id TEXT NOT NULL,
  solve_time_seconds INTEGER NOT NULL,
  solved_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
""")


@asynccontextmanager
async def fastapi_lifespan(app:FastAPI):
    app.db_pool = AsyncConnectionPool(conninfo=os.getenv("DATABASE_URL"),open=False)
    await app.db_pool.open()
    # app.db_pool = AsyncConnectionPool(conninfo=os.getenv("DATABASE_URL"))
    await db_create_tables(app.db_pool)
    yield
    await app.db_pool.close()


# Lifespan only applies to top-level instances:
#  https://fastapi.tiangolo.com/advanced/events/#sub-applications
root = FastAPI(lifespan=fastapi_lifespan)
api  = FastAPI()

root.mount("/api", api)
root.mount("/", StaticFiles(directory="public",html=True), name="static")



########################################
# API ROUTES and VIEWS                 #
########################################
def map_puzzle_to_response(p:Puzzle.Puzzle):
    return {
        "id": p.id,
        "labels": {
            "A": p.criteria[0].label,
            "B": p.criteria[1].label,
            "C": p.criteria[2].label,
        },
    }


@api.get("/puzzles/current")
async def get_current_puzzle():
    """Get the currently-active Puzzle"""
    puzzle = Puzzle.get_current()
    return map_puzzle_to_response(puzzle)


@api.get("/puzzles/{puzzle_id}")
async def get_puzzle_by_id(puzzle_id:str):
    """Get a Puzzle by its ID"""
    puzzle = Puzzle.get_by_id(puzzle_id)
    if not puzzle:
        raise HTTPException(status_code=404, detail="Puzzle not found")
    return map_puzzle_to_response(puzzle)


@api.get("/puzzles/{puzzle_id}/words/{word}")
async def get_word_for_puzzle(puzzle_id:str, word:str):
    """Get details about a word in the context of a given Puzzle"""
    puzzle = Puzzle.get_by_id(puzzle_id)
    if not puzzle:
        raise HTTPException(status_code=404, detail="Puzzle not found")
    if not Puzzle.word_exists(word):
        raise HTTPException(status_code=404, detail="Word does not exist")
    region_id, criteria_matches = puzzle.get_region_for_word(word)
    return {
        "id": str.lower(word),
        "input": word,
        "puzzle_id": puzzle_id,
        "region_id": region_id,
        "region_matches": [match.label for match in criteria_matches]
    }
