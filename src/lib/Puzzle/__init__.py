from datetime import date
from src.lib import Dictionary
from src.lib.Puzzle.Criteria import Criterion
from src.lib.Puzzle.Config import puzzle_config

def get_current() -> Puzzle:
    # Grab the Puzzle with the current date if it exists
    today_id = date.today().isoformat()
    today_puzzle = get_by_id(today_id)
    if today_puzzle:
        return today_puzzle

    # Otherwise, iterate through all of them until we hit a date that has not yet passed
    # Start by sorting the list for good measure (standard YYYY-MM-DD strings sort naturally)...
    sorted_puzzle_config = dict(sorted(puzzle_config.items(), reverse=False))
    # Initialize a fallback by grabbing the earliest date we have...
    (prev_id, prev_crit) = next(iter(sorted_puzzle_config.items()))
    # Now calculate validity as we iterate:
    #  Test to see if today is less than the next entry in the sorted config list
    for next_id, next_crit in sorted_puzzle_config.items():
        # - If it is, don't serve it, as it is for the future. Break in order to return the most-recent as of this point
        if today_id < next_id:
            break
        # - Otherwise, it is valid to serve, so track it as a potential fallback for a future iteration
        prev_id = next_id
        prev_crit = next_crit

    # Finally, return the last found valid config - that is the "current" puzzle
    return Puzzle(prev_id, prev_crit)

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

    def get_criteria_by_mask(self, mask:int) -> list[Criterion]:
        results:list[Criterion] = []
        for i in range(0, len(self.criteria)):
            crit_bit = 1 << i
            if mask & crit_bit:
                results.append(self.criteria[i])
        return results
