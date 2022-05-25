from OTLMOW.Facility.AgentCollection import AgentCollection
from OTLMOW.Facility.DavieExporter import DavieExporter
from OTLMOW.Facility.OTLFacility import OTLFacility
from OTLMOW.Facility.RequesterFactory import RequesterFactory
from OTLMOW.Loggers.ConsoleLogger import ConsoleLogger
from OTLMOW.Loggers.LoggerCollection import LoggerCollection
from OTLMOW.Loggers.TxtLogger import TxtLogger

from UploadAfschermendeConstructies.FSConnector import FSConnector
from UploadAfschermendeConstructies.JsonToEventDataACProcessor import JsonToEventDataACProcessor
from UploadAfschermendeConstructies.MappingTableProcessor import MappingTableProcessor
from UploadAfschermendeConstructies.OffsetGeometryProcessor import OffsetGeometryProcessor
from UploadAfschermendeConstructies.RelationProcessor import RelationProcessor
from UploadAfschermendeConstructies.SettingsManager import SettingsManager

if __name__ == '__main__':
    logger = LoggerCollection([
        TxtLogger(r'C:\temp\pythonLogging\pythonlog.txt'),
        ConsoleLogger()])
    otl_facility = OTLFacility(logger, settings_path='C:\\resources\\settings_OTLMOW.json', enable_relation_features=True)
    settings_manager = SettingsManager(settings_path='C:\\resources\\settings_AWVGedeeldeFuncties.json')
    requester = RequesterFactory.create_requester(settings=settings_manager.settings, auth_type='cert', env='prd')

    fs_c = FSConnector(requester)
    raw_output = fs_c.get_raw_lines(layer="afschermendeconstructies", lines=1000)  # beperkt tot 20

    processor = JsonToEventDataACProcessor()
    listEventDataAC = processor.processJson(raw_output)

    # use relation_processor to search for candidates
    relation_processor = RelationProcessor()
    relation_processor.store(listEventDataAC)
    relation_processor.process_for_candidates()

    ogp = OffsetGeometryProcessor()
    for eventDataAC in listEventDataAC:
        ogp.process_wkt_to_Z(eventDataAC)
        try:
            offset_geometry = ogp.create_offset_geometry_from_eventdataAC(eventDataAC, round_precision=3)
            eventDataAC.offset_wkt = offset_geometry.wkt
            eventDataAC.offset_geometry = offset_geometry
        except:
            pass

    lijst_otl_objecten = []
    mtp = MappingTableProcessor('analyse_afschermende_constructies.xlsx')

    # convert objects in listEventDataAC to OTL conform objects, using the mapping table
    # fill in as much data as possible
    # create heef
    for eventDataAC in listEventDataAC:
        try:
            otl_object = mtp.create_otl_object_from_eventDataAC(eventDataAC)
            if otl_object is None:
                raise ValueError('Could not create an otl object so skipping...')
            otl_object.eventDataAC = eventDataAC
            otl_object.assetId.identificator = eventDataAC.id
            otl_object.assetId.toegekendDoor = 'UploadAfschermendeConstructies'

            # verplaatsen naar jsoneventdataACProcessor
            if 'Agentschap Wegen en Verkeer' in eventDataAC.gebied:
                agent_name = eventDataAC.gebied[-6:]
                agent_name = agent_name[0:3] + "_" + agent_name[-3:]
                agent = AgentCollection(requester=requester).get_agent_by_fulltextsearch_name(agent_name)

                if agent is not None:
                    districtrelatie = otl_facility.relatie_creator.create_betrokkenerelation(bron=otl_object, doel=agent)
                    districtrelatie.rol = 'berekende-beheerder'
                    lijst_otl_objecten.append(districtrelatie)

            lijst_otl_objecten.append(otl_object)
        except Exception as e:
            print(f'{e} => id:{eventDataAC.id} product:{eventDataAC.product} materiaal:{eventDataAC.materiaal}')

    relation_processor.process_for_relations(otl_facility, lijst_otl_objecten)

    # clean up
    for otl_object in lijst_otl_objecten:
        if hasattr(otl_object, 'eventDataAC'):
            delattr(otl_object, 'eventDataAC')

    DavieExporter().export_objects_to_json_file(list_of_objects=lijst_otl_objecten, file_path='DAVIE_export_file.json')

