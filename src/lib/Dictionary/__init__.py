from src.lib import Database

async def word_exists(word:str) -> bool:
    async with Database.get_pool().connection() as conn:
        query = await conn.execute("SELECT word FROM dictionary WHERE word = %s", (word,))
    result = await query.fetchone()
    return bool(result)

async def get_word_count() -> int:
    async with Database.get_pool().connection() as conn:
        query = await conn.execute("SELECT COUNT(*) as count FROM dictionary")
        (count,) = await query.fetchone()
        return int(count)