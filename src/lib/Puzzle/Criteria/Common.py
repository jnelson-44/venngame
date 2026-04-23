
from src.lib.Puzzle.Criteria import Criterion

class EndsWith(Criterion):
    def __init__(self, letters:str):
        super().__init__(f"Ends with {str.upper(letters)}")
        self.letters = letters

    def is_satisfied_by(self, solution:str) -> bool:
        if str.lower(solution[len(solution)-len(self.letters):]) == str.lower(self.letters):
            return True
        return False


class StartsWith(Criterion):
    def __init__(self, letters:str):
        super().__init__(f"Begins with {str.upper(letters)}")
        self.letters = letters

    def is_satisfied_by(self, solution:str) -> bool:
        if str.lower(solution[:len(self.letters)]) == str.lower(self.letters):
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


class Multiplicity(Criterion):
    def __init__(self, n:int, char:str):
        self.n = n
        self.char = str.lower(char)
        super().__init__(f"Has exactly {n} {str.upper(char)}s")

    def is_satisfied_by(self, solution:str) -> bool:
        count = 0
        for char in str.lower(solution):
            if char == self.char:
                count = count + 1
        return count == self.n


class AtLeast(Criterion):
    def __init__(self, n:int, char:str):
        self.n = n
        self.char = str.lower(char)
        super().__init__(f"Has at least {n} {str.upper(char)}s")

    def is_satisfied_by(self, solution:str) -> bool:
        count = 0
        for char in str.lower(solution):
            if char == self.char:
                count = count + 1
        return count >= self.n


class AtMost(Criterion):
    def __init__(self, n:int, char:str):
        self.n = n
        self.char = str.lower(char)
        super().__init__(f"Has at most {n} {str.upper(char)}s")

    def is_satisfied_by(self, solution:str) -> bool:
        count = 0
        for char in str.lower(solution):
            if char == self.char:
                count = count + 1
        return count <= self.n
