import logging
from itertools import combinations

import shapely
import shapely.wkt
from OTLMOW.OTLModel.Classes.Abstracten.Beginstuk import Beginstuk
from OTLMOW.OTLModel.Classes.ImplementatieElement.RelatieObject import RelatieObject
from OTLMOW.OTLModel.Classes.Onderdeel.Bevestiging import Bevestiging
from OTLMOW.OTLModel.Classes.Onderdeel.Eindstuk import Eindstuk
from OTLMOW.OTLModel.Classes.Onderdeel.Geleideconstructie import Geleideconstructie
from OTLMOW.OTLModel.Classes.Onderdeel.Motorvangplank import Motorvangplank
from OTLMOW.OTLModel.Classes.Onderdeel.SluitAanOp import SluitAanOp
from shapely.geometry import box, Point, LineString
from shapely.ops import shared_paths


class RelationProcessor:
    def __init__(self):
        self.events = []

    def store(self, listEventDataAC):
        for eventDataAC in listEventDataAC:
            eventDataAC.shape = shapely.wkt.loads(eventDataAC.wktLineStringZM)
            eventDataAC.related_assets = []
            self.events.append(eventDataAC)

    def process_for_candidates(self, print_number_of_candidates: bool = False):
        for eventDataAC in self.events:
            bounds = eventDataAC.shape.bounds
            bounding_box = box(bounds[0], bounds[1], bounds[2], bounds[3]).buffer(5)
            reduced_group = []
            for other in self.events:
                if other == eventDataAC:
                    continue
                if bounding_box.intersects(other.shape):
                    reduced_group.append(other)
            if print_number_of_candidates:
                print(f'{eventDataAC.id} : {len(reduced_group)}')

            # eventDataAC.candidates = list(map(lambda x: x.id, reduced_group))
            eventDataAC.candidates = reduced_group

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
        assets = list(filter(lambda x: x.typeURI not in ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HeeftBetrokkene'], lijst_otl_objecten))
        for a in assets:
            a.candidates = []
            a.geom = shapely.wkt.loads(a.geometry)

        # loopen door lijst_otl_objecten
        # voor elke object:
        # zijn er candidates?
        for a1, a2 in combinations(assets, 2):
            if a1.geom.intersects(a2.geom):
                a1.candidates.append(a2)

        for otl_asset in assets:
            if len(otl_asset.candidates) == 0:
                continue

            # heeft otl_object en 1 van de candidates een gemeenschappelijk punt?
            for candidate in otl_asset.candidates:
                canditate_geom = candidate.geom

                intersected_geometry = otl_asset.geom.intersection(canditate_geom)
                if intersected_geometry is None:
                    continue

                # doorsnee = punt => nakijken of het begin- en eindpunt zijn, zo ja: SluitAanOp
                if isinstance(intersected_geometry, Point):
                    candidate_first_point = canditate_geom.coords[0]
                    last_candidate = canditate_geom.coords[-1]
                    otl_asset_first_point = otl_asset.geom.coords[0]
                    otl_asset_last_point = otl_asset.geom.coords[-1]

                    if (intersected_geometry.coords[0] == candidate_first_point and intersected_geometry.coords[
                        0] == otl_asset_last_point) or \
                            (intersected_geometry.coords[0] == last_candidate and intersected_geometry.coords[
                                0] == otl_asset_first_point):
                        relatie = None
                        if otl_asset.typeURI == Eindstuk.typeURI and candidate.typeURI == Geleideconstructie.typeURI:
                            relatie = otl_facility.relatie_creator.create_relation(candidate, otl_asset, SluitAanOp)
                        elif otl_asset.typeURI == Geleideconstructie.typeURI and candidate.typeURI == Eindstuk.typeURI:
                            relatie = otl_facility.relatie_creator.create_relation(otl_asset, candidate, SluitAanOp)
                        elif otl_asset.typeURI == Geleideconstructie.typeURI and isinstance(candidate, Beginstuk):
                            relatie = otl_facility.relatie_creator.create_relation(candidate, otl_asset, SluitAanOp)
                        elif isinstance(candidate, Beginstuk) and otl_asset.typeURI == Geleideconstructie.typeURI:
                            relatie = otl_facility.relatie_creator.create_relation(otl_asset, candidate, SluitAanOp)
                        if relatie is None:
                            return
                        bestaande_relatie = next((a for a in lijst_otl_objecten if isinstance(a, RelatieObject) and
                                                  a.bronAssetId.identificator == relatie.bronAssetId.identificator and
                                                  a.doelAssetId.identificator == relatie.doelAssetId.identificator), None)
                        if bestaande_relatie is None:
                            lijst_otl_objecten.append(relatie)
                # doorsnee = lijn => Bevestiging relatie
                elif isinstance(intersected_geometry, LineString):
                    if not ((otl_asset.typeURI == Motorvangplank.typeURI and candidate.typeURI == Geleideconstructie.typeURI) or (otl_asset.typeURI == Geleideconstructie.typeURI and candidate.typeURI == Motorvangplank.typeURI)):
                        return
                    try:
                        if otl_asset.assetId.identificator < candidate.assetId.identificator:
                            relatie = otl_facility.relatie_creator.create_relation(otl_asset, candidate, Bevestiging)
                        else:
                            relatie = otl_facility.relatie_creator.create_relation(candidate, otl_asset, Bevestiging)
                        bestaande_relatie = next((a for a in lijst_otl_objecten if isinstance(a, RelatieObject) and
                                                  a.bronAssetId.identificator == relatie.bronAssetId.identificator and
                                                  a.doelAssetId.identificator == relatie.doelAssetId.identificator), None)
                        if bestaande_relatie is None:
                            lijst_otl_objecten.append(relatie)
                    except:
                        logging.error(
                            f'Could not create a Bevestiging relation between assets: id: {otl_asset.assetId.identificator}, {candidate.assetId.identificator} types:{type(otl_asset)}, {type(candidate)}')
