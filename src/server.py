from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from psycopg_pool import AsyncConnectionPool
import src.lib.Puzzle as Puzzle

########################################
# DATABASE & SERVER INIT               #
########################################
db_pool = AsyncConnectionPool(conninfo=os.getenv("DATABASE_URL"),open=False)
@asynccontextmanager
async def fastapi_lifespan(app:FastAPI):
    await db_pool.open()
    app.state.db_pool = db_pool # This makes it available in all instances of FastAPI
    yield
    await db_pool.close()


# Lifespan only applies to top-level instances:
#  https://fastapi.tiangolo.com/advanced/events/#sub-applications
root = FastAPI(lifespan=fastapi_lifespan)
api  = FastAPI()

root.mount("/api", api)
root.mount("/", StaticFiles(directory="public",html=True), name="static")


# TODO: Move this to the Domain area and make the Database shareable
########################################
# DATABASE HELPERS                     #
########################################
async def word_exists(word:str) -> bool:
    async with db_pool.connection() as conn:
        query = await conn.execute("SELECT word FROM dictionary WHERE word = %s", (word,))
    result = await query.fetchone()
    return bool(result)



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
    if not await word_exists(word):
        raise HTTPException(status_code=404, detail="Word does not exist")
    region_id, criteria_matches = puzzle.get_region_for_word(word)
    return {
        "id": str.lower(word),
        "input": word,
        "puzzle_id": puzzle_id,
        "region_id": region_id,
        "region_matches": [match.label for match in criteria_matches]
    }


# This object describes the shape of the request body for the POSTing of Solutions
class SolutionBody(BaseModel):
    solveTimeSeconds:int

@api.post("/puzzles/{puzzle_id}/solutions")
async def solve_puzzle(puzzle_id:str, s:SolutionBody):
    """Submit a solution for a Puzzle and save it"""
    puzzle = Puzzle.get_by_id(puzzle_id)
    if not puzzle:
        raise HTTPException(status_code=404, detail="Puzzle not found")

    async with db_pool.connection() as conn:
        await conn.execute("""
            INSERT INTO solves (puzzle_id, solve_time_seconds)
            VALUES (%s, %s)
            """, (puzzle_id, s.solveTimeSeconds))

    return { "success": True }

@api.get("/puzzles/{puzzle_id}/stats")
async def get_puzzle_stats(puzzle_id:str):
    """Get play summary for a Puzzle"""
    puzzle = Puzzle.get_by_id(puzzle_id)
    if not puzzle:
        raise HTTPException(status_code=404, detail="Puzzle not found")

    async with db_pool.connection() as conn:
        query = await conn.execute("""
        SELECT
            COUNT(*)::int AS "playersSolved",
            ROUND(AVG(solve_time_seconds))::int AS "averageTime"
        FROM solves
        WHERE puzzle_id = %s
        """, (puzzle_id,))
    players_solved, avg_time = await query.fetchone()

    return {
        "playersSolved": 0 if players_solved is None else players_solved,
        "averageTime": 0 if avg_time is None else avg_time
    }