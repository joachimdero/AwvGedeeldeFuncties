import shapely
import shapely.wkt
from shapely.geometry import box
from shapely.ops import shared_paths


class RelationProcessor:
    def __init__(self):
        self.events = []

    def store(self, listEventDataAC):
        for eventDataAC in listEventDataAC:
            eventDataAC.shape = shapely.wkt.loads(eventDataAC.wktLineStringZM)
            eventDataAC.related_assets = []
            self.events.append(eventDataAC)

    def pre_process(self):
        for eventDataAC in self.events:
            bounds = eventDataAC.shape.bounds
            bounding_box = box(bounds[0], bounds[1], bounds[2], bounds[3]).buffer(5)
            reduced_group = []
            for other in self.events:
                if other == eventDataAC:
                    continue
                if bounding_box.intersects(other.shape):
                    reduced_group.append(other)
            print(f'{eventDataAC.id} : {len(reduced_group)}')

            # door geen offset te gebruiken, risico op verkeerde match tussen gedeelde geometriën waarbij de zijde van de rijbaan verschillend is
            # eventueel oplossen door ident8 te filteren

            for other in reduced_group:
                # hebben een lijnstuk gemeen
                forward = shared_paths(eventDataAC.shape, other.shape)
                ident8_condition_false_match = other.ident8[:7] == eventDataAC.ident8[:7] and other.ident8[-1] != eventDataAC.ident8[-1]
                if forward is not None and len(forward) > 0:
                    if other.ident8 == eventDataAC.ident8 and other.zijde_rijbaan != eventDataAC.zijde_rijbaan:
                        continue
                    if ident8_condition_false_match:
                        continue
                    if other.id not in eventDataAC.related_assets:
                        eventDataAC.related_assets.append(other.id)

                # check for overlap?


        pass

