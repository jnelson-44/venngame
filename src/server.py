from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

####
# SERVER CONFIG
####
root = FastAPI()
api  = FastAPI()

root.mount("/api", api)
root.mount("/", StaticFiles(directory="public",html=True), name="static")



####
# API ROUTES
####
@api.get("/puzzles/current")
async def get_current_puzzle():
    return {
        "puzzleId": "2026-03-25"
    }


