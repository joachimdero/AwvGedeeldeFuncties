import concurrent.futures
import platform
import time
from pathlib import Path

from otlmow_converter.FileExporter import FileExporter
from otlmow_model.Classes.ImplementatieElement.RelatieObject import RelatieObject
from otlmow_model.Helpers import RelationCreator
from termcolor import colored

from UploadAfschermendeConstructies.FSConnector import FSConnector
from UploadAfschermendeConstructies.JsonToEventDataACProcessor import JsonToEventDataACProcessor
from UploadAfschermendeConstructies.MappingTableProcessor import MappingTableProcessor
from UploadAfschermendeConstructies.OTLMOW_Helpers.AgentCollection import AgentCollection
from UploadAfschermendeConstructies.OTLMOW_Helpers.RequesterFactory import RequesterFactory
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


def from_eventDataAC_create_asset_and_betrokkene_relation(event_data_ac):
    try:
        created_otl_objects = mtp.create_otl_objects_from_eventDataAC(event_data_ac)
        if len(created_otl_objects) == 0:
            raise ValueError('Could not create an otl object so skipping...')

        for created_otl_object in created_otl_objects:
            # maak link naar event data op OTL conform object
            created_otl_object.eventDataAC = event_data_ac

            # zoek de beheerder op als Agent
            if 'Agentschap Wegen en Verkeer' in event_data_ac.gebied:
                agent_name = event_data_ac.gebied[-6:]
                agent_name = agent_name[0:3] + "_" + agent_name[-3:]
                agent = AgentCollection(requester=requester).get_agent_by_fulltextsearch_name(agent_name)

                # indien de Agent gevonden is: leg de relatie tussen asset en Agent rol berekende-beheerder
                if agent is not None:
                    agent.assetId = agent.agentId
                    districtrelatie = RelationCreator.create_betrokkenerelation(source=created_otl_object,
                                                                                target=agent, rol='berekende-beheerder')
                    lijst_otl_objecten.append(districtrelatie)

            lijst_otl_objecten.append(created_otl_object)
    except Exception as e:
        print(f'{e} => id:{event_data_ac.id} product:{event_data_ac.product} materiaal:{event_data_ac.materiaal}')


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

    # haal x aantal afschermende constructies uit de feature server
    fs_c = FSConnector(requester)
    # start = time.time()
    # print(colored(f'Connecting to Feature server...', 'green'))
    # raw_output = fs_c.get_raw_lines(layer="afschermendeconstructies", lines=50000)  # beperkt tot X aantal lijnen
    # end = time.time()
    # print(colored(f'Number of lines (afschermendeconstructies) from Feature server: {len(raw_output)}', 'green'))
    # print(colored(f'Time to get input from feature server: {round(end - start, 2)}', 'yellow'))
    raw_output = []
    with open('AC.json') as f:
        raw_output = f.readlines()
    # raw_output = raw_output[0:2000]

    processor = JsonToEventDataACProcessor()

    # verwerk de input van de feature server tot een lijst van EventDataAC objecten
    start = time.time()
    listEventDataAC = processor.process_json_to_list_event_data_ac(raw_output)
    end = time.time()
    print(
        colored(f'Time to process feature server lines to Python dataclass objects: {round(end - start, 2)}', 'yellow'))

    # filter_ids = ['8797', '8796', '8798']
    # listEventDataAC = list(filter(lambda x: x.id in filter_ids, listEventDataAC))

    print(colored(f'Number of event data objects: {len(listEventDataAC)}', 'green'))

    # haal x aantal rijbanen uit de feature server
    # start = time.time()
    # print(colored(f'Connecting to Feature server...', 'green'))
    # raw_output_rijbanen = fs_c.get_raw_lines(layer="rijbanen", lines=50000)  # beperkt tot X aantal lijnen
    # end = time.time()
    # print(colored(f'Number of lines (rijbanen) from Feature server: {len(raw_output_rijbanen)}', 'green'))
    # print(colored(f'Time to get input from feature server: {round(end - start, 2)}', 'yellow'))
    raw_output_rijbanen = []
    with open('rijbanen.json') as f:
        raw_output_rijbanen = f.readlines()
    # raw_output_rijbanen = raw_output_rijbanen[0:2000]

    # verwerk de input van de feature server tot een lijst van EventDataAC objecten
    start = time.time()
    list_rijbanen = processor.process_json_to_list_event_rijbaan(raw_output_rijbanen)
    end = time.time()
    print(
        colored(f'Time to process feature server lines to Python dataclass objects: {round(end - start, 2)}', 'yellow'))

    print(colored(f'Number of event data objects: {len(list_rijbanen)}', 'green'))

    start = time.time()
    ogp = OffsetGeometryProcessor()
    ogp.add_rijbaan_breedte_to_event_data_ac(listEventDataAC, list_rijbanen)
    end = time.time()
    print(colored(f'Time to add rijbaan breedte to ac events: {round(end - start, 2)}', 'yellow'))

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
    print(colored(f'Number of event data objects using rijbaan data to offset: {ogp.use_rijbaan_count}', 'blue'))

    # gebruik MappingTableProcessor om de events om te zetten naar OTL conforme objecten adhv de mapping tabel in Excel
    # vul zoveel mogelijk data in, inclusief attributen
    start = time.time()
    lijst_otl_objecten = []
    mtp = MappingTableProcessor('Afschermende_constructie_WDB_OTL_conform.xlsx')
    end = time.time()
    print(colored(f'Time to create MappingTableProcessor: {round(end - start, 2)}', 'yellow'))

    # using multithreading
    start = time.time()
    executor = concurrent.futures.ThreadPoolExecutor()
    futures = [executor.submit(from_eventDataAC_create_asset_and_betrokkene_relation, event_data_ac=eventDataAC)
               for eventDataAC in listEventDataAC]
    concurrent.futures.wait(futures)

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
            otl_object.bestekPostNummer = [f'begin:{otl_object.eventDataAC.begin.positie}',
                                           f'eind:{otl_object.eventDataAC.eind.positie}',
                                           f'ident8:{otl_object.eventDataAC.ident8}']
            delattr(otl_object, 'eventDataAC')

    print(colored(f'Number of OTL compliant object (assets + relations): {len(lijst_otl_objecten)}', 'green'))

    print_overview_assets(lijst_otl_objecten)

    # gebruik OTLMOW om de OTL conforme objecten weg te schrijven naar een export bestand
    exporter = FileExporter(settings=settings_manager.settings)
    exporter.create_file_from_assets(list_of_objects=lijst_otl_objecten,
                                     filepath=Path('DAVIE_export_file_20230926.json'))
