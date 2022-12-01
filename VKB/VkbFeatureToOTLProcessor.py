from pathlib import Path

from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_converter.RelationCreator import create_relation
from otlmow_model.Classes.Onderdeel.Bevestiging import Bevestiging
from otlmow_model.Classes.Onderdeel.Funderingsmassief import Funderingsmassief
from otlmow_model.Classes.Onderdeel.Verkeersbordsteun import Verkeersbordsteun

from VKB.VkbFeature import VkbFeature


class VkbFeatureToOTLProcessor:
    def process_to_otl(self, features: [VkbFeature], file_path: Path):
        list_of_objects = []

        for feature in features:
            feature_objects = []
            for f_steun in feature.steunen:
                v = None
                if f_steun.type_key == 1: # Steun
                    v = Verkeersbordsteun()
                    v.type = 'rechte-paal'
                elif f_steun.type_key == 10: # Andere
                    continue
                if v is not None:
                    feature_objects.append(v)
                    v.geometry = feature.wktPoint
                    if f_steun.diameter != -1:
                        v.diameter.waarde = f_steun.diameter
                    if f_steun.lengte != -1:
                        v.lengte.waarde = f_steun.lengte / 1000.0
                    if f_steun.diameter != -1:
                        v.diameter.waarde = f_steun.diameter
                    v.assetId.identificator = f'{feature.id}_steun_{f_steun.id}'

                sokkel = None
                if f_steun.sokkel_key == 1:
                    sokkel = Funderingsmassief()
                    sokkel.materiaal = 'beton'
                    sokkel.afmetingGrondvlak.rechthoekig.lengte.waarde = 30
                    sokkel.afmetingGrondvlak.rechthoekig.breedte.waarde = 30
                if sokkel is not None:
                    feature_objects.append(sokkel)
                    sokkel.geometry = feature.wktPoint
                    sokkel.assetId.identificator = f'{feature.id}_steun_{f_steun.id}_sokkel'

                if v is not None and sokkel is not None:
                    feature_objects.append(create_relation(source=sokkel, target=v, relation=Bevestiging))

            list_of_objects.extend(feature_objects)

        otlmow_converter = OtlmowConverter()
        otlmow_converter.create_file_from_assets(list_of_objects=list_of_objects, filepath=file_path)
