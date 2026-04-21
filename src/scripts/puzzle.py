import asyncio
import os
import typer
from rich import print
from src.lib import Database, Puzzle
from typing import Annotated

app = typer.Typer(no_args_is_help=True)

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
## SCRIPT COMMAND: GET REGION HITS       ##
###########################################
BATCH_SIZE:int = 500

@app.command("get-region-hits")
def region_hits(
        puzzle_id: Annotated[str, typer.Argument(metavar="PUZZLE", help="The ID of the puzzle to evaluate")],
        dsn:       Annotated[str, typer.Option(help="The DSN string of the database (e.g., type://user:pass@host:port/dbname). If not provided, the DATABASE_URL environment variable must be set")] = None,
        batchsize: Annotated[int, typer.Option(help=f"Number of words to evaluate at a time (defaults to {BATCH_SIZE})")] = BATCH_SIZE,
    ):
    asyncio.run(_region_hits(puzzle_id, get_dsn(dsn), batchsize))


async def _region_hits(puzzle_id:str, dsn:str, batch_size:int):
    print(f"""Compiling Region Hit information for Puzzle {puzzle_id}...""")

    puzzle = Puzzle.get_by_id(puzzle_id)
    if not puzzle:
        print(f"Puzzle {puzzle_id} not found")
        exit(1)

    hits = [0] * 8

    Database.init(dsn)
    async with Database.get_pool() as pool:
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT COUNT(*) as "count" FROM dictionary
                """)
                (total_words,) = await cur.fetchone()
                offset = 0

                while offset < total_words:
                    async with conn.cursor() as cur:
                        await cur.execute("""
                            SELECT * FROM dictionary WHERE id > %(offset)s ORDER BY id LIMIT %(limit)s
                        """, { "offset": offset, "limit": batch_size })
                        results = await cur.fetchall()
                        for (id, word) in results:
                            region = puzzle.get_region_for_word(word)[0]
                            hits[region] = hits[region] + 1
                    offset = offset + batch_size

    print(f"""
Puzzle Name: [bold green]{puzzle.id}[/bold green]

[bold grey50]Region A:[/bold grey50] {puzzle.criteria[0].label}
[bold grey50]Region B:[/bold grey50] {puzzle.criteria[1].label}
[bold grey50]Region C:[/bold grey50] {puzzle.criteria[2].label}

         A: {hits[1]:6}
         B: {hits[2]:6}
         C: {hits[4]:6}
     A & B: {hits[3]:6}
     B & C: {hits[6]:6}
     C & A: {hits[5]:6}
 A & B & C: {hits[7]:6}
      None: {hits[0]:6}
                """)

###########################################
## SCRIPT COMMAND: GET PUZZLE INFO       ##
###########################################
@app.command()
def info(
        puzzle_id: Annotated[str, typer.Argument(metavar="PUZZLE", help="The ID of the puzzle to evaluate")],
    ):
    puzzle = Puzzle.get_by_id(puzzle_id)
    if not puzzle:
        print(f"Puzzle {puzzle_id} not found")
        exit(1)

    print(f"""
Puzzle Name: [bold green]{puzzle.id}[/bold green]

[bold grey50]Region A:[/bold grey50] {puzzle.criteria[0].label}
[bold grey50]Region B:[/bold grey50] {puzzle.criteria[1].label}
[bold grey50]Region C:[/bold grey50] {puzzle.criteria[2].label}
    """)


###########################################
## SCRIPT COMMAND: GET REGION MASK       ##
###########################################
@app.command("get-region-mask")
def region_mask(
        region_ids:   Annotated[str, typer.Argument(metavar="REGIONS",help="The Region(s) to pull words for")],
    ):
    print(_region_mask(region_ids))

def _region_mask(region_ids:str):
    region_ids = set(region_ids.upper())
    mask = 0
    mask_dict = {"A": 1, "B": 2, "C": 4}
    for char in region_ids:
        mask = mask + mask_dict[char]
    return mask


###########################################
## SCRIPT COMMAND: GET REGION WORDS      ##
###########################################
@app.command("get-region-words")
def region_words(
        puzzle_id: Annotated[str, typer.Argument(metavar="PUZZLE", help="The ID of the puzzle to evaluate")],
        region_ids:Annotated[str, typer.Argument(metavar="REGIONS",help="The Region(s) to pull words for")],
        dsn:       Annotated[str, typer.Option(help="The DSN string of the database (e.g., type://user:pass@host:port/dbname). If not provided, the DATABASE_URL environment variable must be set")] = None,
        batchsize: Annotated[int, typer.Option(help=f"Number of words to evaluate at a time (defaults to {BATCH_SIZE})")] = BATCH_SIZE,
        outfile:   Annotated[str, typer.Option(help="The absolute or relative path of a file to write the results to (writes to STDOUT otherwise)")] = None,
    ):
    asyncio.run(_region_words(puzzle_id, region_ids, get_dsn(dsn), batchsize, outfile))


async def _region_words(puzzle_id:str, region_ids:str, dsn:str, batch_size:int, outfile:str):
    puzzle = Puzzle.get_by_id(puzzle_id)
    if not puzzle:
        print(f"Puzzle {puzzle_id} not found")
        exit(1)

    region_mask = _region_mask(region_ids)
    hits = []

    Database.init(dsn)
    async with Database.get_pool() as pool:
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT COUNT(*) as "count" FROM dictionary
                                  """)
                (total_words,) = await cur.fetchone()
                offset = 0

                while offset < total_words:
                    async with conn.cursor() as cur:
                        await cur.execute("""
                            SELECT * FROM dictionary WHERE id > %(offset)s ORDER BY id LIMIT %(limit)s
                                          """, {"offset": offset, "limit": batch_size})
                        results = await cur.fetchall()
                        for (id, word) in results:
                            region = puzzle.get_region_for_word(word)[0]
                            if region == region_mask:
                                hits.append(word)
                    offset = offset + batch_size

    if outfile is None:
        print("\n".join(hits))
        return

    with open(outfile, "w", encoding="utf-8") as file:
        file.write("\n".join(hits))



###########################################
## SCRIPT ROOT INVOCATION                ##
###########################################

if __name__ == "__main__":
    app()
