import dataclasses

from UploadAfschermendeConstructies.WegLocatieData import WegLocatieData


@dataclasses.dataclass
class EventDataAC:
    zijde_rijbaan: str = ''
    afstand_rijbaan: float = -1.0
    ident8: str = ''
    wktLineStringZM: str = ''
    begin: WegLocatieData = WegLocatieData()
    eind: WegLocatieData = WegLocatieData()
    typeAC : str = ''
    product : str = ''
