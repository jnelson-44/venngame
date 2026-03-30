from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import src.lib.Puzzle as Puzzle

########################################
# SERVER CONFIG                        #
########################################
root = FastAPI()
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
