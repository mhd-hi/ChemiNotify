from enum import Enum


class StateType(Enum):
    """Enum representing all possible application states"""

    INITIAL = "INITIAL"
    LOGIN = "LOGIN"
    CONSULTATION = "CONSULTATION"
    INSCRIPTION = "INSCRIPTION"
    SELECTION_COURS = "SELECTION_COURS"
    HORAIRE = "HORAIRE"
    EXIT = "EXIT"
    ERROR = "ERROR"

    def __str__(self) -> str:
        return self.value
