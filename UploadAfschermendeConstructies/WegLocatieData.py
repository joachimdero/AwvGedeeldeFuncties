import dataclasses


@dataclasses.dataclass
class WegLocatieData:
    positie: float = 0
    bron: str = ''
    wktPoint: str = ''