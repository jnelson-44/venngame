import asyncio
import re
import typer
from rich import print
from src.lib import Database, Puzzle, Dictionary
from typing import Annotated
from .common import get_dsn, get_puzzle

app = typer.Typer(no_args_is_help=True)

BATCH_SIZE:int = 500

###########################################
## SCRIPT COMMAND: GET REGION HITS       ##
###########################################
@app.command("get-region-hits")
def region_hits(
        puzzle_id: Annotated[str, typer.Argument(metavar="PUZZLE", help="The ID of the puzzle to evaluate")],
        dsn:       Annotated[str, typer.Option(help="The DSN string of the database (e.g., type://user:pass@host:port/dbname). If not provided, the DATABASE_URL environment variable must be set")] = None,
        batchsize: Annotated[int, typer.Option(help=f"Number of words to evaluate at a time")] = BATCH_SIZE,
    ):
    asyncio.run(_region_hits(puzzle_id, get_dsn(dsn), batchsize))


async def _region_hits(puzzle_id:str, dsn:str, batch_size:int):
    print(f"""Compiling Region Hit information for Puzzle {puzzle_id}...""")

    puzzle = get_puzzle(puzzle_id)
    hits = [0] * 8

    Database.init(dsn)
    async with Database.get_pool() as pool:
        total_words = await Dictionary.get_word_count()
        offset = 0
        async with pool.connection() as conn:
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

Mask   Region:   Hits
(1)         A: {hits[1]:6}
(2)         B: {hits[2]:6}
(4)         C: {hits[4]:6}
(3)     A & B: {hits[3]:6}
(6)     B & C: {hits[6]:6}
(5)     C & A: {hits[5]:6}
(7) A & B & C: {hits[7]:6}
(0)      None: {hits[0]:6}
                """)

###########################################
## SCRIPT COMMAND: GET PUZZLE INFO       ##
###########################################
@app.command()
def info(
        puzzle_id: Annotated[str, typer.Argument(metavar="PUZZLE", help="The ID of the puzzle to evaluate")],
    ):
    puzzle = get_puzzle(puzzle_id)

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
        region_ids: Annotated[str, typer.Argument(metavar="REGIONS",help="The Region(s), as single string in any order.  E.g., 'B', 'AC', 'BCA', etc")],
        puzzle_id:  Annotated[str, typer.Option(metavar="PUZZLE", help="If provided, displays region label(s) in addition to the mask")] = None,
    ):
    region_mask = _region_mask(region_ids)[0]
    print(f"{region_mask}")
    crit_output = None
    if puzzle_id:
        puzzle = get_puzzle(puzzle_id)
        criteria = puzzle.get_criteria_by_mask(region_mask)
        for crit in criteria:
            print(crit.label)


def _region_mask(region_ids:str) -> tuple[int, str]:
    if not re.fullmatch(r"[ABC]+", region_ids.upper()):
        print("Invalid region specified: Must be A, B, and/or C")
        exit(1)
    region_ids = set(region_ids.upper())
    mask = 0
    mask_dict = {"A": 1, "B": 2, "C": 4}
    for char in region_ids:
        mask = mask + mask_dict[char]
    return mask, "".join(sorted(region_ids))


###########################################
## SCRIPT COMMAND: EXPORT REGION WORDS   ##
###########################################
@app.command("export-region-words")
def region_words(
        puzzle_id:  Annotated[str, typer.Argument(help="The ID of the puzzle to evaluate")],
        region_ids: Annotated[str, typer.Argument(help="The Region(s) to pull words for, as single string in any order.  E.g., 'B', 'AC', 'BCA', etc")],
        dsn:        Annotated[str, typer.Option(help="The DSN string of the database (e.g., type://user:pass@host:port/dbname). If not provided, the DATABASE_URL environment variable must be set")] = None,
        batchsize:  Annotated[int, typer.Option(help=f"Number of words to evaluate at a time")] = BATCH_SIZE,
        outfile:    Annotated[str, typer.Option(help="The absolute or relative path of a file to write the results to (writes to STDOUT otherwise)")] = None,
    ):
    asyncio.run(_region_words(puzzle_id, region_ids, get_dsn(dsn), batchsize, outfile))


async def _region_words(puzzle_id:str, region_ids:str, dsn:str, batch_size:int, outfile:str):
    puzzle = get_puzzle(puzzle_id)
    (region_mask, normalized_ids) = _region_mask(region_ids)
    hits = []

    print(f"\nAggregating words for region(s) '{normalized_ids}' (mask {region_mask}) with Criteria:")
    criteria = puzzle.get_criteria_by_mask(region_mask)
    for crit in criteria:
        print(f"   - {crit.label}")
    print()

    Database.init(dsn)
    async with Database.get_pool() as pool:
        total_words = await Dictionary.get_word_count()
        offset = 0
        async with pool.connection() as conn:
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
    print(f"{len(hits)} results written to {outfile}")



###########################################
## SCRIPT ROOT INVOCATION                ##
###########################################

if __name__ == "__main__":
    app()
