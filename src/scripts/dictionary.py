import asyncio
import typer
from pathlib import Path
from psycopg_pool import AsyncConnectionPool
from rich import print
from src.lib import Database, Dictionary
from typing import Annotated
from .common import get_dsn

app = typer.Typer(no_args_is_help=True)

BATCH_SIZE:int = 500

###########################################
## DATABASE HELPERS                      ##
###########################################
async def db_table_dictionary_clear(pool:AsyncConnectionPool) -> None:
    """
    Drops the dictionary table, if it exists
    """
    async with pool.connection() as conn:
        await conn.execute("""
TRUNCATE TABLE dictionary RESTART IDENTITY
""")


###########################################
## SCRIPT COMMAND: IMPORT                ##
###########################################

@app.command("import")
def db_import(
        filename:  Annotated[str, typer.Argument(help="The absolute or relative path to the dictionary.txt file")],
        dsn:       Annotated[str, typer.Option(help="The DSN string of the database (e.g., type://user:pass@host:port/dbname). If not provided, the DATABASE_URL environment variable must be set")] = None,
        batchsize: Annotated[int, typer.Option(help=f"Size of batches to use")] = BATCH_SIZE,
        debug:     Annotated[bool, typer.Option(help="Print debug output")] = False
    ):
    """
    Takes the Dictionary defined in FILENAME and imports it into the database.
    """
    asyncio.run(_db_import(filename, get_dsn(dsn), batchsize, debug))


async def _db_import(file:str, dsn:str, batch_size:int=BATCH_SIZE, debug:bool=False):
    print(f"""Generating dictionary table from {file} in batches of size {batch_size}""")
    if debug: print("Debug mode enabled")

    if not Path(file).exists():
        print(f"Unable to locate file {file}")
        exit(1)

    Database.init(dsn)
    async with Database.get_pool() as pool:
        if debug: print("Clearing dictionary table")
        await db_table_dictionary_clear(pool)

        async def insert_batch(cur, batch, debug=False):
            if debug: print("Inserting batch")
            await cur.executemany(
                "INSERT INTO dictionary (word) VALUES (%s) ON CONFLICT DO NOTHING",
                batch
            )

        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                batch = []
                count = 0
                with open(file, "r") as f:
                    for line in f:
                        word = line.strip()
                        if not word:
                            continue
                        word = word.lower()
                        batch.append((word,))
                        count = count + 1
                        if debug: print(f"Queuing {word}")

                        if len(batch) >= batch_size:
                            await insert_batch(cur, batch, debug)
                            batch.clear()
                    if len(batch) > 0:
                        await insert_batch(cur, batch, debug)
            await conn.commit()
            print(f"""[green]DONE.[/green] Inserted {count} words into the dictionary table""")


###########################################
## SCRIPT COMMAND: NORMALIZE             ##
###########################################

@app.command("normalize")
def file_normalize(
        filename: Annotated[str, typer.Argument(help="The absolute or relative path to the dictionary.txt file")],
    ):
    """
    Prints the normalized dictionary from the given file as it would be imported into the database.
    """
    if not Path(filename).exists():
        print(f"Unable to locate file {filename}")
        exit(1)

    with open(filename, "r") as f:
        for line in f:
            word = line.strip()
            if not word:
                continue
            word = word.lower()
            print(word)


###########################################
## SCRIPT COMMAND: COUNT                 ##
###########################################
@app.command()
def count(
        dsn: Annotated[str, typer.Option(help="The DSN string of the database (e.g., type://user:pass@host:port/dbname). If not provided, the DATABASE_URL environment variable must be set")] = None,
    ):
    """
    Returns the number of words in the current dictionary database
    """
    asyncio.run(_count(get_dsn(dsn)))

async def _count(dsn:str):
    Database.init(dsn)
    async with Database.get_pool():
        print(await Dictionary.get_word_count())



###########################################
## SCRIPT ROOT INVOCATION                ##
###########################################

if __name__ == "__main__":
    app()
