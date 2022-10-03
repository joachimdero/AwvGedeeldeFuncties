import platform
import time

from OTLMOW.Facility.OTLFacility import OTLFacility
from OTLMOW.Facility.RequesterFactory import RequesterFactory
from termcolor import colored

from UploadAfschermendeConstructies.RelationProcessor import RelationProcessor
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


if __name__ == '__main__':
    if platform.system() == 'Linux':
        OTLMOW_settings_path = '/home/davidlinux/Documents/AWV/resources/settings_OTLMOW.json'
        this_settings_path = '/home/davidlinux/Documents/AWV/resources/settings_AWVGedeeldeFuncties.json'
    else:
        OTLMOW_settings_path = 'C:\\resources\\settings_OTLMOW.json'
        this_settings_path = 'C:\\resources\\settings_AWVGedeeldeFuncties.json'

    # een aantal classes uit OTLMOW library gebruiken
    otl_facility = OTLFacility(logfile='', settings_path=OTLMOW_settings_path, enable_relation_features=True)
    settings_manager = SettingsManager(settings_path=this_settings_path)
    requester = RequesterFactory.create_requester(settings=settings_manager.settings, auth_type='cert', env='prd')

    start = time.time()
    lijst_otl_objecten = otl_facility.create_assets_from_file(filepath='DAVIE_export_file_20221003.json')
    end = time.time()
    print(colored(f'Time to load otl {len(lijst_otl_objecten)} assets: {round(end - start, 2)}', 'yellow'))

    # gebruik RelationProcessor om relaties te leggen tussen de verschillende objecten
    start = time.time()
    relation_processor = RelationProcessor()
    relation_processor.process_for_relations(otl_facility, lijst_otl_objecten)
    end = time.time()
    print(colored(f'Time to process for relations: {round(end - start, 2)}', 'yellow'))

    # opkuis: tijdelijk attribuut eventDataAC op OTL conform object weghalen
    for otl_object in lijst_otl_objecten:
        if hasattr(otl_object, 'candidates'):
            delattr(otl_object, 'candidates')
        if hasattr(otl_object, 'geom'):
            delattr(otl_object, 'geom')
        if hasattr(otl_object, 'index'):
            delattr(otl_object, 'index')
        if hasattr(otl_object, 'relation_id'):
            delattr(otl_object, 'relation_id')

    print(colored(f'Number of OTL compliant object (assets + relations): {len(lijst_otl_objecten)}', 'green'))

    print_overview_assets(lijst_otl_objecten)

    # gebruik OTLMOW om de OTL conforme objecten weg te schrijven naar een export bestand
    otl_facility.create_file_from_assets(list_of_objects=lijst_otl_objecten, filepath='DAVIE_export_file_20221001.json')
