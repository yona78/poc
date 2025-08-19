from dataclasses import dataclass


@dataclass(frozen=True)
class Company:
    id: int
    name: str
