
from src.lib.Puzzle.Criteria import Criterion

class EndsWithLetter(Criterion):
    def __init__(self, letter:str):
        super().__init__(f"Ends with {str.upper(letter)}")
        self.letter = letter

    def is_satisfied_by(self, solution:str) -> bool:
        if str.lower(solution[-1]) == str.lower(self.letter):
            return True
        return False


class StartsWithLetter(Criterion):
    def __init__(self, letter:str):
        super().__init__(f"Must begin with the letter {letter}")
        self.letter = letter

    def is_satisfied_by(self, solution:str) -> bool:
        if str.lower(solution[0]) == str.lower(self.letter):
            return True
        return False


class HasDoubleLetters(Criterion):
    def __init__(self):
        super().__init__("Has double letters")

    def is_satisfied_by(self, solution:str) -> bool:
        prev_letter:str = solution[0]
        for i in range(1, len(solution)):
            if str.lower(solution[i]) == str.lower(prev_letter):
                return True
            prev_letter = solution[i]
        return False