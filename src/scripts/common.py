import os

from src.lib import Puzzle


###########################################
## DATABASE HELPERS                      ##
###########################################
def get_dsn(dsn:str=None) -> str:
    """
    Returns the DSN passed in, if it exists, or returns the DATABASE_URL environment variable
    """
    if dsn:
        return dsn
    dsn = os.getenv("VENNGAME_DATABASE_URL") \
        if os.getenv("VENNGAME_DATABASE_URL") is not None \
        else os.getenv("DATABASE_URL")
    if not dsn:
        print("Must provide --dsn option or DATABASE_URL (or VENNGAME_DATABASE_URL) environment variable")
        exit(1)
    return dsn

###########################################
## PUZZLE HELPERS                        ##
###########################################
def get_puzzle(puzzle_id:str) -> Puzzle.Puzzle:
    puzzle = Puzzle.get_by_id(puzzle_id)
    if not puzzle:
        print(f"Puzzle {puzzle_id} not found")
        exit(1)
    return puzzle