from src.lib import Dictionary
from src.lib.Puzzle.Criteria import Criterion
from src.lib.Puzzle.Config import puzzle_config

def get_current() -> Puzzle:
    # Grabbing the first one in the list for now
    puzz_id, crit = next(iter(puzzle_config.items()))
    return Puzzle(puzz_id,crit)

def get_by_id(puzz_id:str) -> Puzzle | None:
    if puzz_id in puzzle_config:
        return Puzzle(puzz_id, puzzle_config[puzz_id])
    return None

class Puzzle:
    def __init__(self, id:str, criteria:list[Criterion]):
        self.id = id
        self.criteria = criteria

    def get_region_for_word(self, word:str) -> tuple[int, list[Criterion]]:
        mask:int = 0
        matches:list[Criterion] = []
        for i in range(0, len(self.criteria)):
            region_bit:int = 1 << i
            if self.criteria[i].is_satisfied_by(word):
                mask = mask + region_bit
                matches.append(self.criteria[i])
        return mask, matches

    async def solve_with(self, inputs:list[str]) -> bool:
        expected_region_count = 7
        if len(inputs) != expected_region_count:
            raise ValueError(f"Solution incomplete: Expecting {expected_region_count} words but received {len(inputs)}")
        regions_found = set()
        for i in range(0, len(inputs)):
            if not await Dictionary.word_exists(inputs[i]):
                raise ValueError(f"Solution incomplete. Invalid word \"{inputs[i]}\" found in submission.")
            region_id = self.get_region_for_word(inputs[i])[0]
            if region_id == 0:
                raise ValueError(f"Solution incomplete: Word \"{inputs[i]}\" matches no criteria.")
            if region_id in regions_found:
                raise ValueError(f"Solution incomplete: Region {region_id} overloaded.")
            regions_found.add(region_id)
        return len(regions_found) == expected_region_count
