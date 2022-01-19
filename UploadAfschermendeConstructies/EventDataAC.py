import dataclasses

from UploadAfschermendeConstructies.WegLocatieData import WegLocatieData


@dataclasses.dataclass
class EventDataAC:
    ident8: str = ''
    wktLineStringZM: str = ''
    begin: WegLocatieData = WegLocatieData()
    eind: WegLocatieData = WegLocatieData()
