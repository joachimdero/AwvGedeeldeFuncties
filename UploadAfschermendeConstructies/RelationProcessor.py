import concurrent.futures

import shapely
import shapely.wkt
from otlmow_model.Classes.Onderdeel.Bevestiging import Bevestiging
from otlmow_model.Classes.Onderdeel.Eindstuk import Eindstuk
from otlmow_model.Classes.Onderdeel.Geleideconstructie import Geleideconstructie
from otlmow_model.Classes.Onderdeel.GetesteBeginconstructie import GetesteBeginconstructie
from otlmow_model.Classes.Onderdeel.Motorvangplank import Motorvangplank
from otlmow_model.Classes.Onderdeel.NietGetestBeginstuk import NietGetestBeginstuk
from otlmow_model.Classes.Onderdeel.Obstakelbeveiliger import Obstakelbeveiliger
from otlmow_model.Classes.Onderdeel.Overgangsconstructie import Overgangsconstructie
from otlmow_model.Classes.Onderdeel.SluitAanOp import SluitAanOp
from rtree import index
from shapely.geometry import Point, LineString

from UploadAfschermendeConstructies.OTLMOW_Helpers.RelationCreator import RelationCreator


class RelationProcessor:
    def __init__(self):
        self.otl_facility = None
        self.assets = None
        self.lijst_otl_objecten = None
        self.events = []

        self.relation_mapping = {
            (Geleideconstructie.typeURI, Eindstuk.typeURI, 'point'): (1, 2, SluitAanOp),
            (Eindstuk.typeURI, Geleideconstructie.typeURI, 'point'): (2, 1, SluitAanOp),

            # TODO https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#NietConformBegin
            (GetesteBeginconstructie.typeURI, Geleideconstructie.typeURI, 'point'): (1, 2, SluitAanOp),
            (Geleideconstructie.typeURI, GetesteBeginconstructie.typeURI, 'point'): (2, 1, SluitAanOp),
            (NietGetestBeginstuk.typeURI, Geleideconstructie.typeURI, 'point'): (1, 2, SluitAanOp),
            (Geleideconstructie.typeURI, NietGetestBeginstuk.typeURI, 'point'): (2, 1, SluitAanOp),

            # TODO https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#NietConformBegin
            (GetesteBeginconstructie.typeURI, Overgangsconstructie.typeURI, 'point'): (1, 2, SluitAanOp),
            (Overgangsconstructie.typeURI, GetesteBeginconstructie.typeURI, 'point'): (2, 1, SluitAanOp),
            (NietGetestBeginstuk.typeURI, Overgangsconstructie.typeURI, 'point'): (1, 2, SluitAanOp),
            (Overgangsconstructie.typeURI, NietGetestBeginstuk.typeURI, 'point'): (2, 1, SluitAanOp),

            (Overgangsconstructie.typeURI, Geleideconstructie.typeURI, 'point'): (1, 2, SluitAanOp),
            (Geleideconstructie.typeURI, Overgangsconstructie.typeURI, 'point'): (1, 2, SluitAanOp),

            (Geleideconstructie.typeURI, Obstakelbeveiliger.typeURI, 'point'): (1, 2, SluitAanOp),
            (Obstakelbeveiliger.typeURI, Geleideconstructie.typeURI, 'point'): (2, 1, SluitAanOp),
            (Overgangsconstructie.typeURI, Obstakelbeveiliger.typeURI, 'point'): (1, 2, SluitAanOp),
            (Obstakelbeveiliger.typeURI, Overgangsconstructie.typeURI, 'point'): (2, 1, SluitAanOp),

            (Geleideconstructie.typeURI, Motorvangplank.typeURI, 'line'): (1, 2, Bevestiging),
            (Motorvangplank.typeURI, Geleideconstructie.typeURI, 'line'): (2, 1, Bevestiging),
            (Overgangsconstructie.typeURI, Motorvangplank.typeURI, 'line'): (1, 2, Bevestiging),
            (Motorvangplank.typeURI, Overgangsconstructie.typeURI, 'line'): (2, 1, Bevestiging),
        }

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

    def process_for_relations(self, lijst_otl_objecten):
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
        self.new_relations = []

        # use multithreading
        executor = concurrent.futures.ThreadPoolExecutor()
        futures = [executor.submit(self.process_asset_to_create_relation, otl_asset=otl_asset) for otl_asset in assets]
        concurrent.futures.wait(futures)

        cleaned_relations = self.clean_double_relations(self.new_relations)

        self.lijst_otl_objecten.extend(cleaned_relations)

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

            # doorsnee = punt => nakijken of het begin- of eindpunt is, zo ja: SluitAanOp
            if isinstance(intersected_geometry, Point):
                candidate_first_point = canditate_geom.coords[0]
                last_candidate = canditate_geom.coords[-1]
                otl_asset_first_point = otl_asset.geom.coords[0]
                otl_asset_last_point = otl_asset.geom.coords[-1]

                if (intersected_geometry.coords[0] == candidate_first_point and intersected_geometry.coords[
                    0] == otl_asset_last_point) or \
                        (intersected_geometry.coords[0] == last_candidate and intersected_geometry.coords[
                            0] == otl_asset_first_point):

                    relatie = self.create_relation_based_on_types(asset1=otl_asset, asset2=candidate,
                                                                  intersected_geometry='point')
                    if relatie is None:
                        continue
                    self.new_relations.append(relatie)

            # doorsnee = lijn => Bevestiging relatie
            elif isinstance(intersected_geometry, LineString):
                relatie = self.create_relation_based_on_types(asset1=otl_asset, asset2=candidate,
                                                              intersected_geometry='line')
                if relatie is None:
                    continue
                self.new_relations.append(relatie)

    def clean_double_relations(self, new_relations):
        for relation in new_relations:
            if relation.bronAssetId.identificator < relation.doelAssetId.identificator:
                relation.relation_id = relation.bronAssetId.identificator + relation.doelAssetId.identificator + relation.typeURI
            else:
                relation.relation_id = relation.doelAssetId.identificator + relation.bronAssetId.identificator + relation.typeURI

        return {r.relation_id: r for r in new_relations}.values()

    def create_relation_based_on_types(self, asset1, asset2, intersected_geometry):
        try:
            relation_params = self.relation_mapping[(asset1.typeURI, asset2.typeURI, intersected_geometry)]
            if relation_params[0] == 1:
                return RelationCreator.create_relation(asset1, asset2, relation_params[2])
            else:
                return RelationCreator.create_relation(asset2, asset1, relation_params[2])
        except KeyError:
            pass

        return None
