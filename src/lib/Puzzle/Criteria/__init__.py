from abc import ABC, abstractmethod

def _lower_first(s:str) -> str:
    return s[0].lower() + s[1:]

class Criterion(ABC):
    def __init__(self, label:str):
        self.label = label

    @abstractmethod
    def is_satisfied_by(self, solution:str) -> bool:
        pass

    def Labeled(self, label:str) -> Criterion:
        self.label = label
        return self

    def And(self, crit:Criterion) -> Intersection:
        return Intersection(self, crit)

    def Or(self, crit:Criterion) -> Union:
        return Union(self, crit)


class Negation(Criterion):
    def __init__(self, a:Criterion, label:str = None):
        self.a = a
        if label is None:
            label = f"Not {_lower_first(a.label)}"
        super().__init__(label)

    def is_satisfied_by(self, solution:str) -> bool:
        return not self.a.is_satisfied_by(solution)


class Intersection(Criterion):
    def __init__(self, a:Criterion, b:Criterion, label:str = None):
        self.a = a
        self.b = b
        if label is None:
            label = f"{a.label} and {_lower_first(b.label)}"
        super().__init__(label)

    def is_satisfied_by(self, solution:str) -> bool:
        return self.a.is_satisfied_by(solution) and self.b.is_satisfied_by(solution)

class Union(Criterion):
    def __init__(self, a:Criterion, b:Criterion, label:str = None):
        self.a = a
        self.b = b
        if label is None:
            label = f"{a.label} or {_lower_first(b.label)}"
        super().__init__(label)

    def is_satisfied_by(self, solution:str) -> bool:
        return self.a.is_satisfied_by(solution) or self.b.is_satisfied_by(solution)

class Not(Negation):
    pass

class And(Intersection):
    pass

class Or(Union):
    pass
