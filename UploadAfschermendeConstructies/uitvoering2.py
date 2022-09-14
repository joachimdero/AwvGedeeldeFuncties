import platform

from OTLMOW.Facility.AgentCollection import AgentCollection
from OTLMOW.Facility.OTLFacility import OTLFacility
from OTLMOW.Facility.RequesterFactory import RequesterFactory
from OTLMOW.OTLModel.Classes.ImplementatieElement.RelatieObject import RelatieObject
from OTLMOW.OTLModel.Classes.Onderdeel.Bevestiging import Bevestiging
from OTLMOW.OTLModel.Classes.Onderdeel.SluitAanOp import SluitAanOp
from termcolor import colored


from UploadAfschermendeConstructies.FSConnector import FSConnector
from UploadAfschermendeConstructies.JsonToEventDataACProcessor import JsonToEventDataACProcessor
from UploadAfschermendeConstructies.MappingTableProcessor import MappingTableProcessor
from UploadAfschermendeConstructies.OffsetGeometryProcessor import OffsetGeometryProcessor
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

        # gebruik RelationProcessor om kandidaten voor relaties alvast op te lijsten op de asset zelf
    relation_processor = RelationProcessor()

    lijst_otl_objecten = otl_facility.create_assets_from_file(filepath='DAVIE_export_file_20220912.json')

    # gebruik RelationProcessor om relaties te leggen tussen de verschillende objecten
    relation_processor.process_for_relations(otl_facility, lijst_otl_objecten)

    # opkuis: tijdelijk attribuut eventDataAC op OTL conform object weghalen
    for otl_object in lijst_otl_objecten:
        if hasattr(otl_object, 'candidates'):
            delattr(otl_object, 'candidates')
        if hasattr(otl_object, 'geom'):
            delattr(otl_object, 'geom')
        if hasattr(otl_object, 'index'):
            delattr(otl_object, 'index')

    print(colored(f'Number of OTL compliant object (assets + relations): {len(lijst_otl_objecten)}', 'green'))

    print_overview_assets(lijst_otl_objecten)

    # gebruik OTLMOW om de OTL conforme objecten weg te schrijven naar een export bestand
    otl_facility.create_file_from_assets(list_of_objects=lijst_otl_objecten, filepath='DAVIE_export_file_20220913.json')
