import dataclasses

from UploadAfschermendeConstructies.WegLocatieData import WegLocatieData


@dataclasses.dataclass
class EventRijbaan:
    wegcategorie: str = ''
    ident8: str = ''
    aantal_rijstroken: int = -1
    rijrichting: str = ''
    id: str = ''
    lengte: int = -1
    breedte_rijbaan: int = -1
    opmerking: str = ''
    wktLineStringZM: str = ''
    wktLineStringZ: str = ''
    begin: WegLocatieData = WegLocatieData()
    eind: WegLocatieData = WegLocatieData()
