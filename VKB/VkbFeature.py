import dataclasses

from VKB.VkbBevestiging import VkbBevestiging
from VKB.VkbBord import VkbBord
from VKB.VkbSteun import VkbSteun


@dataclasses.dataclass
class VkbFeature:
    id: int = -1
    wktPoint: str = ''
    external_id: str = ''
    client_id: str = ''
    borden: [VkbBord] = None
    bevestigingen: [VkbBevestiging] = None
    steunen: [VkbSteun] = None
    beheerder_key: int = -1
