import platform
import time

from OTLMOW.Facility.AgentCollection import AgentCollection
from OTLMOW.Facility.OTLFacility import OTLFacility
from OTLMOW.Facility.RequesterFactory import RequesterFactory
from OTLMOW.OTLModel.Classes.ImplementatieElement.RelatieObject import RelatieObject
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

    # haal x aantal afschermende constructies uit de feature server
    fs_c = FSConnector(requester)
    start = time.time()
    print(colored(f'Connecting to Feature server...', 'green'))
    raw_output = fs_c.get_raw_lines(layer="afschermendeconstructies", lines=30000)  # beperkt tot X aantal lijnen
    end = time.time()
    print(colored(f'Number of lines from Feature server: {len(raw_output)}', 'green'))
    print(colored(f'Time to get input from feature server: {round(end - start, 2)}', 'yellow'))

    # verwerk de input van de feature server tot een lijst van EventDataAC objecten
    start = time.time()
    processor = JsonToEventDataACProcessor()
    listEventDataAC = processor.processJson(raw_output)
    end = time.time()
    print(colored(f'Time to process feature server lines to Python dataclass objects: {round(end - start, 2)}', 'yellow'))

    #filter_ids = ['8797', '8796', '8798']
    #listEventDataAC = list(filter(lambda x: x.id in filter_ids, listEventDataAC))

    print(colored(f'Number of event data objects: {len(listEventDataAC)}', 'green'))

    # gebruik RelationProcessor om kandidaten voor relaties alvast op te lijsten op de asset zelf
    start = time.time()
    relation_processor = RelationProcessor()
    relation_processor.store(listEventDataAC)
    relation_processor.process_for_candidates(print_number_of_candidates=False)
    end = time.time()
    print(
        colored(f'Time to process objects for candidates (optimize offset points): {round(end - start, 2)}',
                'yellow'))

    # gebruik OffsetGeometryProcessor om de geometrieën van de events te verschuiven, afhankelijk van de event data.
    start = time.time()
    ogp = OffsetGeometryProcessor()
    offset_gefaald_teller = 0
    for eventDataAC in listEventDataAC:
        ogp.process_wkt_to_Z(eventDataAC)
        try:
            offset_geometry = ogp.create_offset_geometry_from_eventdataAC(eventDataAC, round_precision=3)
            eventDataAC.offset_wkt = offset_geometry.wkt
            eventDataAC.offset_geometry = offset_geometry
        except:
            offset_gefaald_teller += 1
    print(colored(f'Aantal gefaalde offsets: {offset_gefaald_teller}', 'red'))
    end = time.time()
    print(colored(f'Time to offset lines depending on event data: {round(end - start, 2)}', 'yellow'))

    # punten kunnen niet geoffset worden, wordt apart verschoven indien er exact 1 match voor de offset was
    start = time.time()
    for eventDataAC in listEventDataAC:
        if not eventDataAC.needs_offset:
            continue
        ogp.try_fixing_points_via_relations(eventDataAC)

    offset_count = sum(1 for e in listEventDataAC if not e.needs_offset)
    end = time.time()
    print(colored(f'Time to offset points using offset of a related asset: {round(end - start, 2)}', 'yellow'))
    print(colored(f'Number of event data objects with an offset geometry: {offset_count}', 'green'))


    # gebruik MappingTableProcessor om de events om te zetten naar OTL conforme objecten adhv de mapping tabel in Excel
    # vul zoveel mogelijk data in, inclusief attributen
    start = time.time()
    lijst_otl_objecten = []
    mtp = MappingTableProcessor('Afschermende_constructie_WDB_OTL_conform.xlsx')
    end = time.time()
    print(colored(f'Time to create MappingTableProcessor: {round(end - start, 2)}', 'yellow'))

    start = time.time()
    for eventDataAC in listEventDataAC:
        try:
            otl_object_list = mtp.create_otl_objects_from_eventDataAC(eventDataAC)
            if len(otl_object_list) == 0:
                raise ValueError('Could not create an otl object so skipping...')

            for otl_object in otl_object_list:
                # maak link naar event data op OTL conform object
                otl_object.eventDataAC = eventDataAC

                # zoek de beheerder op als Agent
                if 'Agentschap Wegen en Verkeer' in eventDataAC.gebied:
                    agent_name = eventDataAC.gebied[-6:]
                    agent_name = agent_name[0:3] + "_" + agent_name[-3:]
                    agent = AgentCollection(requester=requester).get_agent_by_fulltextsearch_name(agent_name)

                    # indien de Agent gevonden is: leg de relatie tussen asset en Agent rol berekende-beheerder
                    if agent is not None:
                        districtrelatie = otl_facility.relatie_creator.create_betrokkenerelation(bron=otl_object, doel=agent)
                        districtrelatie.rol = 'berekende-beheerder'
                        lijst_otl_objecten.append(districtrelatie)

                lijst_otl_objecten.append(otl_object)
        except Exception as e:
            print(f'{e} => id:{eventDataAC.id} product:{eventDataAC.product} materiaal:{eventDataAC.materiaal}')
    end = time.time()
    print(colored(f'Time to create OTL compliant assets and betrokkene relations: {round(end - start, 2)}', 'yellow'))

    assets = list(filter(lambda a: not isinstance(a, RelatieObject), lijst_otl_objecten))
    print(colored(f'Number of OTL compliant assets: {len(assets)}', 'green'))

    # gebruik RelationProcessor om relaties te leggen tussen de verschillende objecten
    # relation_processor.process_for_relations(otl_facility, lijst_otl_objecten)
    # dit wordt gedaan in uitvoering2.py

    # opkuis: tijdelijk attribuut eventDataAC op OTL conform object weghalen
    for otl_object in lijst_otl_objecten:
        if hasattr(otl_object, 'eventDataAC'):
            delattr(otl_object, 'eventDataAC')

    print(colored(f'Number of OTL compliant object (assets + relations): {len(lijst_otl_objecten)}', 'green'))

    print_overview_assets(lijst_otl_objecten)

    # gebruik OTLMOW om de OTL conforme objecten weg te schrijven naar een export bestand
    otl_facility.create_file_from_assets(list_of_objects=lijst_otl_objecten, filepath='DAVIE_export_file_20220914.json')
