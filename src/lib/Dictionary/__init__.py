from src.lib import Database

async def word_exists(word:str) -> bool:
    async with Database.get_pool().connection() as conn:
        query = await conn.execute("SELECT word FROM dictionary WHERE word = %s", (word,))
    result = await query.fetchone()
    return bool(result)
