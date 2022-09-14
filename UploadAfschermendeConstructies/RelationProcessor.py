import logging
from itertools import combinations
import geopandas as gpd

import shapely
import shapely.wkt
from OTLMOW.OTLModel.Classes.Abstracten.Beginstuk import Beginstuk
from OTLMOW.OTLModel.Classes.ImplementatieElement.RelatieObject import RelatieObject
from OTLMOW.OTLModel.Classes.Onderdeel.Bevestiging import Bevestiging
from OTLMOW.OTLModel.Classes.Onderdeel.Eindstuk import Eindstuk
from OTLMOW.OTLModel.Classes.Onderdeel.Geleideconstructie import Geleideconstructie
from OTLMOW.OTLModel.Classes.Onderdeel.Motorvangplank import Motorvangplank
from OTLMOW.OTLModel.Classes.Onderdeel.SluitAanOp import SluitAanOp
from rtree import index
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
        idx = index.Index()

        for i, eventDataAC in enumerate(self.events):
            eventDataAC.index = i
            bb = eventDataAC.shape.bounds
            idx.insert(i, bb)

        for eventDataAC in self.events:
            eventDataAC.candidates = []
            candidate_indeces = list(idx.intersection(eventDataAC.shape.bounds, objects=True))
            for c in candidate_indeces:
                if eventDataAC.id == self.events[c.id].id:
                    continue
                eventDataAC.candidates.append(self.events[c.id])

            if print_number_of_candidates:
                print(f'{eventDataAC.id} : {len(eventDataAC.candidates)}')

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
        idx = index.Index()

        assets = list(filter(
            lambda x: x.typeURI not in ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HeeftBetrokkene'],
            lijst_otl_objecten))
        for i, a in enumerate(assets):
            a.candidates = []
            a.index = i
            a.geom = shapely.wkt.loads(a.geometry)
            bb = a.geom.bounds
            idx.insert(i, bb)

        print('assets now have geometries in .geom')

        # gebruik combinations om de candidates voor elk asset vast te leggen
        for asset in assets:
            asset.candidates = list(idx.intersection(asset.geom.bounds, objects=True))

        print('assets now have candidates')

        # loopen door assets
        # voor elke object:
        # zijn er candidates?
        for counter, otl_asset in enumerate(assets):
            if counter % 100 == 0:
                print(f'processed {counter} assets')
            if len(otl_asset.candidates) == 0:
                continue

            # heeft otl_object en 1 van de candidates een gemeenschappelijk punt?
            for candidate_index in otl_asset.candidates:
                candidate = assets[candidate_index.id]
                if candidate.assetId.identificator == otl_asset.assetId.identificator:
                    continue
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
                            continue
                        bestaande_relatie = next((a for a in lijst_otl_objecten if isinstance(a, RelatieObject) and
                                                  a.bronAssetId.identificator == relatie.bronAssetId.identificator and
                                                  a.doelAssetId.identificator == relatie.doelAssetId.identificator),
                                                 None)
                        if bestaande_relatie is None:
                            lijst_otl_objecten.append(relatie)
                            print(f'added relation of type {relatie.typeURI} between {otl_asset.assetId.identificator} and {candidate.assetId.identificator}')
                # doorsnee = lijn => Bevestiging relatie
                elif isinstance(intersected_geometry, LineString):
                    if not ((
                                    otl_asset.typeURI == Motorvangplank.typeURI and candidate.typeURI == Geleideconstructie.typeURI) or (
                                    otl_asset.typeURI == Geleideconstructie.typeURI and candidate.typeURI == Motorvangplank.typeURI)):
                        continue
                    try:
                        if otl_asset.assetId.identificator < candidate.assetId.identificator:
                            relatie = otl_facility.relatie_creator.create_relation(otl_asset, candidate, Bevestiging)
                        else:
                            relatie = otl_facility.relatie_creator.create_relation(candidate, otl_asset, Bevestiging)
                        bestaande_relatie = next((a for a in lijst_otl_objecten if isinstance(a, RelatieObject) and
                                                  a.bronAssetId.identificator == relatie.bronAssetId.identificator and
                                                  a.doelAssetId.identificator == relatie.doelAssetId.identificator),
                                                 None)
                        if bestaande_relatie is None:
                            lijst_otl_objecten.append(relatie)
                            print(f'added relation of type {relatie.typeURI} between {otl_asset.assetId.identificator} and {candidate.assetId.identificator}')
                    except:
                        logging.error(
                            f'Could not create a Bevestiging relation between assets: id: {otl_asset.assetId.identificator}, {candidate.assetId.identificator} types:{type(otl_asset)}, {type(candidate)}')
