from abc import ABC, abstractmethod

class Criterion(ABC):
    def __init__(self, label:str):
        self.label = label

    @abstractmethod
    def is_satisfied_by(self, solution:str) -> bool:
        pass