import shapely
import shapely.wkt
from OTLMOW.OTLModel.Classes.Eindstuk import Eindstuk
from OTLMOW.OTLModel.Classes.RelatieObject import RelatieObject
from OTLMOW.OTLModel.Classes.SluitAanOp import SluitAanOp
from shapely.geometry import box, Point
from shapely.ops import shared_paths


class RelationProcessor:
    def __init__(self):
        self.events = []

    def store(self, listEventDataAC):
        for eventDataAC in listEventDataAC:
            eventDataAC.shape = shapely.wkt.loads(eventDataAC.wktLineStringZM)
            eventDataAC.related_assets = []
            self.events.append(eventDataAC)

    def process_for_candidates(self):
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

            eventDataAC.candidates = list(map(lambda x: x.id, reduced_group))

            # door geen offset te gebruiken, risico op verkeerde match tussen gedeelde geometriën waarbij de zijde van de rijbaan verschillend is
            # eventueel oplossen door ident8 te filteren

            # for other in reduced_group:
            #     # hebben een lijnstuk gemeen
            #     forward = shared_paths(eventDataAC.shape, other.shape)
            #     ident8_condition_false_match = other.ident8[:7] == eventDataAC.ident8[:7] and other.ident8[-1] != eventDataAC.ident8[-1]
            #     if forward is not None and len(forward) > 0:
            #         if other.ident8 == eventDataAC.ident8 and other.zijde_rijbaan != eventDataAC.zijde_rijbaan:
            #             continue
            #         if ident8_condition_false_match:
            #             continue
            #         if other.id not in eventDataAC.related_assets:
            #             eventDataAC.related_assets.append(other.id)

                # check for overlap?


        pass

    def process_for_relations(self, otl_facility, lijst_otl_objecten):
        # loopen door lijst_otl_objecten
        # voor elke object:
        # zijn er candidates?
        for otl_asset in list(filter(lambda r: not isinstance(r, RelatieObject), lijst_otl_objecten)):
            if otl_asset.eventDataAC is None or otl_asset.eventDataAC.candidates is None or len(otl_asset.eventDataAC.candidates) == 0:
                continue
            otl_asset_geom = otl_asset.eventDataAC.offset_geometry

            # heeft otl_object en 1 van de candidates een gemeenschappelijk punt?
            for candidate in otl_asset.eventDataAC.candidates:
                candidate_object = next((a for a in lijst_otl_objecten if a.assetId.identificator == candidate), None)
                if candidate_object is None:
                    continue
                canditate_geom = candidate_object.eventDataAC.offset_geometry

                if otl_asset_geom.touches(canditate_geom):
                    col = otl_asset_geom.intersection(canditate_geom)
                    if isinstance(col, Point):
                        pass
                        first_candidate, last_candidate = canditate_geom.boundary
                        first_otl_asset, last_otl_asset = otl_asset_geom.boundary

                        if (col.equals(first_candidate) and col.equals(last_otl_asset)) or (col.equals(last_candidate) and col.equals(first_otl_asset)):
                            if isinstance(otl_asset, Eindstuk):
                                relatie = otl_facility.relatie_creator.create_relation(candidate_object, otl_asset, SluitAanOp)
                            else:
                                relatie = otl_facility.relatie_creator.create_relation(otl_asset, candidate_object, SluitAanOp)
                            bestaande_relatie = next((a for a in lijst_otl_objecten if isinstance(a, RelatieObject) and
                                                      a.bronAssetId.identificator == relatie.bronAssetId.identificator and
                                                      a.doelAssetId.identificator == relatie.doelAssetId.identificator), None)
                            if bestaande_relatie is None:
                                lijst_otl_objecten.append(relatie)
                            pass
                    pass

                # intersect => 1 punt
                # touches and not overlaps

                pass

            # een relatie aanmaken tussen die 2 objecten

        # # eerst motorvangplanken filteren


