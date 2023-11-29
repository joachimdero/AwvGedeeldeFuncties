import concurrent.futures
import logging
import platform
import time
from pathlib import Path

from otlmow_converter.FileExporter import FileExporter
from otlmow_converter.FileImporter import FileImporter
from otlmow_model.Classes.ImplementatieElement.RelatieObject import RelatieObject
from otlmow_model.Classes.Onderdeel.Eindstuk import Eindstuk
from otlmow_model.Classes.Onderdeel.NietConformBegin import NietConformBegin
from otlmow_model.Classes.Onderdeel.SluitAanOp import SluitAanOp
from termcolor import colored

from UploadAfschermendeConstructies.OTLMOW_Helpers.RequesterFactory import RequesterFactory
from UploadAfschermendeConstructies.SettingsManager import SettingsManager


def print_overview_assets(lijst_otl_objecten):
    overview = {}
    for asset in lijst_otl_objecten:
        if asset.typeURI not in overview:
            overview[asset.typeURI] = 1
        else:
            overview[asset.typeURI] += 1
    for k, v in overview.items():
        print(colored(f'created {str(v)} assets of type {k}', 'blue'))


class BeginstukProcessor:
    def __init__(self):
        self.new_objects = []
        self.objects_to_delete = []

    def process_eindstuk(self, eindstuk):
        if not isinstance(eindstuk, Eindstuk):
            return
        if not hasattr(eindstuk, 'relaties'):
            return
        if len(eindstuk.relaties) > 1:
            logging.error(f'meer dan 1 relatie met dit eindstuk?: {eindstuk.assetId.identificator}')
            return
        bron = eindstuk.relaties[0].bron_asset

        for el in eindstuk.bestekPostNummer:
            if el.startswith('begin'):
                eindstuk_begin = float(el.split(':')[1])
            elif el.startswith('eind'):
                eindstuk_einde = float(el.split(':')[1])
            elif el.startswith('ident8'):
                eindstuk_ident8 = el.split(':')[1]

        for el in bron.bestekPostNummer:
            if el.startswith('begin'):
                bron_begin = float(el.split(':')[1])
            elif el.startswith('eind'):
                bron_einde = float(el.split(':')[1])

        if abs(bron_einde - eindstuk_begin) <= 0.005 and eindstuk_ident8.endswith('2'):
            d = eindstuk.create_dict_from_asset()
            del d['bestekPostNummer']
            del d['typeURI']
            if hasattr(d, 'productidentificatiecode'):
                del d['productidentificatiecode']
            nieuwe_asset = NietConformBegin.from_dict(d)
            self.objects_to_delete.append(eindstuk)
            self.new_objects.append(nieuwe_asset)
            return
        if abs(eindstuk_einde - bron_begin) <= 0.005 and eindstuk_ident8.endswith('1'):
            # fix eindstuk
            d = eindstuk.create_dict_from_asset()

            eindstuk.relaties[0].bronAssetId, eindstuk.relaties[0].doelAssetId = eindstuk.relaties[0].doelAssetId, eindstuk.relaties[0].bronAssetId

            del d['bestekPostNummer']
            del d['typeURI']
            if hasattr(d, 'productidentificatiecode'):
                del d['productidentificatiecode']
            nieuwe_asset = NietConformBegin.from_dict(d)
            self.objects_to_delete.append(eindstuk)
            self.new_objects.append(nieuwe_asset)

    def process_for_beginstukken(self, lijst_otl_objecten):
        asset_dict = { asset.assetId.identificator: asset for asset in lijst_otl_objecten if not isinstance(asset, RelatieObject)}

        for rel in lijst_otl_objecten:
            if not isinstance(rel, SluitAanOp):
                continue
            bron = asset_dict[rel.bronAssetId.identificator]
            doel = asset_dict[rel.doelAssetId.identificator]

            rel.bron_asset = bron
            rel.doel_asset = doel

            if not hasattr(bron, 'relaties'):
                bron.relaties = []
            if not hasattr(doel, 'relaties'):
                doel.relaties = []
            bron.relaties.append(rel)
            doel.relaties.append(rel)

        executor = concurrent.futures.ThreadPoolExecutor()
        futures = [executor.submit(self.process_eindstuk, eindstuk=eindstuk) for eindstuk in lijst_otl_objecten]
        concurrent.futures.wait(futures)

        print(f'{len(self.objects_to_delete)} objects to delete')
        ids_to_delete = list(map(lambda x: x.assetId.identificator, self.objects_to_delete))
        lijst_otl_objecten = [a for a in lijst_otl_objecten if a.assetId.identificator not in ids_to_delete]

        print(f'{len(self.new_objects)} objects to add')
        lijst_otl_objecten.extend(self.new_objects)
        return lijst_otl_objecten


if __name__ == '__main__':
    if platform.system() == 'Linux':
        OTLMOW_settings_path = '/home/davidlinux/Documents/AWV/resources/settings_OTLMOW.json'
        this_settings_path = 'settings_OTLMOW_linux.json'
    else:
        OTLMOW_settings_path = 'C:\\resources\\settings_OTLMOW.json'
        this_settings_path = 'C:\\resources\\settings_AWVGedeeldeFuncties.json'

    # een aantal classes uit OTLMOW library gebruiken
    settings_manager = SettingsManager(settings_path=this_settings_path)
    requester = RequesterFactory.create_requester(settings=settings_manager.settings, auth_type='cert', env='prd')

    start = time.time()
    importer = FileImporter(settings=settings_manager.settings)
    lijst_otl_objecten = importer.create_assets_from_file(filepath=Path('DAVIE_export_file_20231005_2.json'))
    end = time.time()
    print(colored(f'Time to load otl {len(lijst_otl_objecten)} assets: {round(end - start, 2)}', 'yellow'))

    # gebruik RelationProcessor om relaties te leggen tussen de verschillende objecten
    start = time.time()
    relation_processor = BeginstukProcessor()
    lijst_otl_objecten = relation_processor.process_for_beginstukken(lijst_otl_objecten)
    end = time.time()
    print(colored(f'Time to process for relations: {round(end - start, 2)}', 'yellow'))

    # opkuis: tijdelijk attribuut eventDataAC op OTL conform object weghalen
    for otl_object in lijst_otl_objecten:
        if hasattr(otl_object, 'relaties'):
            delattr(otl_object, 'relaties')
        if hasattr(otl_object, 'bron_asset'):
           delattr(otl_object, 'bron_asset')
        if hasattr(otl_object, 'doel_asset'):       
           delattr(otl_object, 'doel_asset')
        if hasattr(otl_object, 'bestekPostNummer'):
            otl_object.bestekPostNummer = []

    print(colored(f'Number of OTL compliant object (assets + relations): {len(lijst_otl_objecten)}', 'green'))

    print_overview_assets(lijst_otl_objecten)

    # gebruik OTLMOW om de OTL conforme objecten weg te schrijven naar een export bestand
    exporter = FileExporter(settings=settings_manager.settings)
    exporter.create_file_from_assets(list_of_objects=lijst_otl_objecten,
                                     filepath=Path('DAVIE_export_file_20231005_3.json'))
