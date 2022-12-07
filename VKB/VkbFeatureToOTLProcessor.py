from pathlib import Path

from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_converter.RelationCreator import create_relation
from otlmow_model.Classes.Installatie.Onderbord import Onderbord
from otlmow_model.Classes.Installatie.VerkeersbordConcept import VerkeersbordConcept
from otlmow_model.Classes.Installatie.VerkeersbordVerkeersteken import VerkeersbordVerkeersteken
from otlmow_model.Classes.Onderdeel.Bevestiging import Bevestiging
from otlmow_model.Classes.Onderdeel.Bevestigingsbeugel import Bevestigingsbeugel
from otlmow_model.Classes.Onderdeel.Funderingsmassief import Funderingsmassief
from otlmow_model.Classes.Onderdeel.HoortBij import HoortBij
from otlmow_model.Classes.Onderdeel.RetroreflecterendVerkeersbord import RetroreflecterendVerkeersbord
from otlmow_model.Classes.Onderdeel.RetroreflecterendeFolie import RetroreflecterendeFolie
from otlmow_model.Classes.Onderdeel.Verkeersbordsteun import Verkeersbordsteun
from otlmow_model.Datatypes.DtuAfmetingVerkeersbord import DtuAfmetingVerkeersbordWaarden

from VKB.VkbBord import VkbBord
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
                    v.assetId.identificator = f'{feature.id}_steun_{f_steun.client_id}'

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

            for f_bord in feature.borden:
                if f_bord.bord_code[0] == 'G':
                    bord = Onderbord()
                else:
                    bord = RetroreflecterendVerkeersbord()
                feature_objects.append(bord)
                bord.aanzicht.waarde = f_bord.aanzicht_hoek
                if f_bord.plaatsing_datum is not None:
                    bord.datumOprichtingObject = f_bord.plaatsing_datum
                bord.assetId.identificator = f'{feature.id}_bord_{f_bord.id}'
                bord.opstelhoogte.waarde = f_bord.y / 1000.0  # TODO waarde wsl niet correct

                self.get_bord_afmeting(bord, f_bord)

                folie = RetroreflecterendeFolie()
                feature_objects.append(folie)
                folie.assetId.identificator = f'{feature.id}_steun_{f_bord.id}_folie'
                if f_bord.folie_type in ['1', '2']:
                    folie.folietype = 'folietype-' + f_bord.folie_type
                feature_objects.append(create_relation(source=bord, target=folie, relation=Bevestiging))

                # TODO verkeersteken
                teken = VerkeersbordVerkeersteken()
                teken.assetId.identificator = f'{feature.id}_verkeersteken_{f_bord.id}'
                if f_bord.bord_code[0] == 'G':
                    teken.variabelOpschrift = '\n'.join(f_bord.parameters)
                feature_objects.append(teken)
                feature_objects.append(create_relation(source=bord, target=teken, relation=HoortBij))

                # TODO verkeersbordconcept
                # niet dubbel aanmaken indien onderbord: hoort bij een bestaand concept
                concept = VerkeersbordConcept()
                concept.assetId.identificator = f'{feature.id}_concept_{f_bord.id}'
                try:
                    if f_bord.bord_code[0] in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'M'] and \
                            f_bord.bord_code not in ['FtsRt', 'E9a-GVIId', 'Gxx']:

                        concept.verkeersbordCode = f_bord.bord_code  # TODO aanvullen keuzelijsten
                except ValueError as exc:
                    print(exc)
                # concept.verkeersbordCategorie  # TODO aanvullen keuzelijsten
                feature_objects.append(concept)
                feature_objects.append(create_relation(source=teken, target=concept, relation=HoortBij))


            for index, f_bevestiging in enumerate(feature.bevestigingen):
                # zoek bord
                bord_found = next((o for o in feature_objects if o.assetId.identificator ==
                                   f'{feature.id}_bord_{f_bevestiging.bord_id}'), None)
                if bord_found is None:
                    NotImplementedError(feature)
                    continue

                # find steun
                for steun_id in f_bevestiging.steun_ids:
                    steun_found = next((o for o in feature_objects if o.assetId.identificator ==
                                       f'{feature.id}_steun_{steun_id}'), None)
                    if steun_found is None:
                        NotImplementedError(feature)
                        continue

                    bb = Bevestigingsbeugel()
                    bb.assetId.identificator = f'{feature.id}_bb_{index}_{f_bevestiging.bord_id}_{steun_id}'
                    feature_objects.append(bb)
                    feature_objects.append(create_relation(source=bb, target=bord_found, relation=Bevestiging))
                    feature_objects.append(create_relation(source=bb, target=steun_found, relation=Bevestiging))

            list_of_objects.extend(feature_objects)

        otlmow_converter = OtlmowConverter()
        otlmow_converter.create_file_from_assets(list_of_objects=list_of_objects, filepath=file_path)

    @staticmethod
    def get_bord_afmeting(bord: RetroreflecterendVerkeersbord, f_bord: VkbBord) -> None:
        if f_bord.vorm == 'rh':  # rechthoek
            bord.afmeting.vierhoekig.breedte.waarde = f_bord.breedte
            bord.afmeting.vierhoekig.hoogte.waarde = f_bord.hoogte
        elif f_bord.vorm == 'rt':
            if f_bord.breedte != f_bord.hoogte:
                raise ValueError(f_bord)
            if f_bord.breedte not in [400, 700, 900, 1100]:
                raise ValueError(f_bord)
            # bord.afmeting.vierhoekig.diagonaal.waarde = f_bord.breedte  # TODO
        elif f_bord.vorm == 'ah':
            if f_bord.breedte != f_bord.hoogte:
                raise ValueError(f_bord)
            if f_bord.breedte not in [150, 400, 700, 900]:  # TODO 150 niet in SB
                raise ValueError(f_bord)
            bord.afmeting.achthoekig.zijde.waarde = f_bord.breedte
        elif f_bord.vorm in ['dh', 'odh']:  # driehoek of omgekeerde driehoek
            if f_bord.breedte != f_bord.hoogte:
                raise ValueError(f_bord)
            if f_bord.breedte not in [400, 700, 900, 1100]:
                raise ValueError(f_bord)
            bord.afmeting.driehoekig.zijde.waarde = f_bord.breedte
        elif f_bord.vorm == 'ro':  # rond
            if f_bord.breedte != f_bord.hoogte:
                raise ValueError(f_bord)
            if f_bord.breedte not in [250, 400, 600, 700, 900, 1100]:  # TODO 250, 600 niet in SB
                raise ValueError(f_bord)
            bord.afmeting.rond.diameter.waarde = f_bord.breedte
        elif f_bord.vorm in ['wwl', 'wwr']:  # wegwijzer
            valid_dimension = False

            valid_dimension = VkbFeatureToOTLProcessor.check_dimensions(f_bord.breedte, f_bord.hoogte, valid_dimension)
            if not valid_dimension:
                f_bord.hoogte, f_bord.breedte = f_bord.breedte, f_bord.hoogte
                valid_dimension = VkbFeatureToOTLProcessor.check_dimensions(f_bord.breedte, f_bord.hoogte, valid_dimension)

            if valid_dimension:
                # bord.afmeting.vierhoekig.breedte.waarde = f_bord.breedte  # TODO
                pass
            else:
                raise ValueError(f_bord)

    @staticmethod
    def check_dimensions(breedte, hoogte, valid_dimension):
        if breedte == 200 and hoogte in [850, 1000, 1150, 1300]:
            valid_dimension = True
        elif breedte == 300 and hoogte in [1250, 1500, 1750, 2000]:
            valid_dimension = True
        elif breedte == 400 and hoogte in [1500, 1750, 2000, 2250, 2500, 2750, 3000]:
            valid_dimension = True
        elif breedte == 500 and hoogte in [2500, 3000, 3500]:
            valid_dimension = True
        elif breedte == 600 and hoogte in [1500, 1750, 2000]:
            valid_dimension = True
        elif breedte == 800 and hoogte in [1500, 1750, 2000, 2250, 2500, 2750, 3000]:
            valid_dimension = True
        return valid_dimension
