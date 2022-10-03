import concurrent.futures
import logging

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
from shapely.geometry import Point, LineString


class RelationProcessor:
    def __init__(self):
        self.otl_facility = None
        self.assets = None
        self.lijst_otl_objecten = None
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

        self.lijst_otl_objecten = lijst_otl_objecten
        self.assets = assets
        self.otl_facility = otl_facility
        self.new_relations = []

        # use multithreading
        executor = concurrent.futures.ThreadPoolExecutor()
        futures = [executor.submit(self.process_asset_to_create_relation, otl_asset=otl_asset) for otl_asset in assets]
        concurrent.futures.wait(futures)

        # for otl_asset in assets:
        #     self.process_asset_to_create_relation(otl_asset)

        self.new_relations = self.clean_double_relations(self.new_relations)

        self.lijst_otl_objecten.extend(self.new_relations)

    def process_asset_to_create_relation(self, otl_asset):
        if len(otl_asset.candidates) == 0:
            return

        # heeft otl_object en 1 van de candidates een gemeenschappelijk punt?
        for candidate_index in otl_asset.candidates:
            candidate = self.assets[candidate_index.id]
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
                        relatie = self.otl_facility.relatie_creator.create_relation(candidate, otl_asset, SluitAanOp)
                    elif otl_asset.typeURI == Geleideconstructie.typeURI and candidate.typeURI == Eindstuk.typeURI:
                        relatie = self.otl_facility.relatie_creator.create_relation(otl_asset, candidate, SluitAanOp)
                    elif otl_asset.typeURI == Geleideconstructie.typeURI and isinstance(candidate, Beginstuk):
                        relatie = self.otl_facility.relatie_creator.create_relation(candidate, otl_asset, SluitAanOp)
                    elif isinstance(candidate, Beginstuk) and otl_asset.typeURI == Geleideconstructie.typeURI:
                        relatie = self.otl_facility.relatie_creator.create_relation(otl_asset, candidate, SluitAanOp)
                    if relatie is None:
                        continue

                    self.new_relations.append(relatie)
            # doorsnee = lijn => Bevestiging relatie
            elif isinstance(intersected_geometry, LineString):
                if not ((
                                otl_asset.typeURI == Motorvangplank.typeURI and candidate.typeURI == Geleideconstructie.typeURI) or (
                                otl_asset.typeURI == Geleideconstructie.typeURI and candidate.typeURI == Motorvangplank.typeURI)):
                    continue
                try:
                    if otl_asset.assetId.identificator < candidate.assetId.identificator:
                        relatie = self.otl_facility.relatie_creator.create_relation(otl_asset, candidate, Bevestiging)
                    else:
                        relatie = self.otl_facility.relatie_creator.create_relation(candidate, otl_asset, Bevestiging)

                    self.new_relations.append(relatie)
                except:
                    logging.error(
                        f'Could not create a Bevestiging relation between assets: id: {otl_asset.assetId.identificator}, {candidate.assetId.identificator} types:{type(otl_asset)}, {type(candidate)}')

    def clean_double_relations(self, new_relations):
        for relation in new_relations:
            if relation.bronAssetId.identificator < relation.doelAssetId.identificator:
                relation.relation_id = relation.bronAssetId.identificator + relation.doelAssetId.identificator + relation.typeURI
            else:
                relation.relation_id = relation.doelAssetId.identificator + relation.bronAssetId.identificator + relation.typeURI

        return {r.relation_id: r for r in new_relations}.values()
