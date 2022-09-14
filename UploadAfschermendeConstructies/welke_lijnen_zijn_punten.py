from datetime import date, datetime

import shapely.wkt
import shapely.ops
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
from UploadAfschermendeConstructies.SettingsManager import SettingsManager

if __name__ == '__main__':
    logger = LoggerCollection([
        TxtLogger(r'C:\temp\pythonLogging\pythonlog.txt'),
        ConsoleLogger()])
    otl_facility = OTLFacility(logger, settings_path='C:\\resources\\settings_OTLMOW.json', enable_relation_features=True)
    settings_manager = SettingsManager(settings_path='C:\\resources\\settings_AWVGedeeldeFuncties.json')
    requester = RequesterFactory.create_requester(settings=settings_manager.settings, auth_type='cert', env='prd')

    fs_c = FSConnector(requester)
    raw_output = fs_c.get_raw_lines(layer="afschermendeconstructies", lines=20)  # beperkt tot 20

    processor = JsonToEventDataACProcessor()
    listEventDataAC = processor.processJson(raw_output)

    ogp = OffsetGeometryProcessor()
    for eventDataAC in listEventDataAC:
        wktString = eventDataAC.wktLineStringZM
        shape = shapely.wkt.loads(wktString)
        new_shape = shapely.ops.transform(lambda x, y, z: (x, y, z), shape)
        new_wkt = new_shape.wkt
        eventDataAC.wktLineStringZM = new_wkt

        begin = shapely.wkt.loads(eventDataAC.begin.wktPoint)
        eind = shapely.wkt.loads(eventDataAC.eind.wktPoint)
        if begin.almost_equals(eind, 0.1):
            # afschermende constructie is een punt: kan alleen maar ge-offset worden indien een gerelateerd asset een offset heeft gekregen
            pass
        # ogp.create_offset_geometry_from_eventdataAC(eventDataAC, round_precision=3)

    lijst_otl_objecten = []
    mtp = MappingTableProcessor('analyse_afschermende_constructies.xlsx')

    for index, eventDataAC in enumerate(listEventDataAC):
        try:
            if eventDataAC.product == 'Duero H2W5 - copro 0634/0002':
                pass

            otl_object = mtp.create_otl_objects_from_eventDataAC(eventDataAC)
            if otl_object is None:
                raise ValueError('Could not create an otl object so skipping...')
            otl_object.assetId.identificator = str(index)
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
            print(f'{e} => product:{eventDataAC.product} materiaal:{eventDataAC.materiaal}')

    DavieExporter().export_objects_to_json_file(list_of_objects=lijst_otl_objecten, file_path='DAVIE_export_file_20220912.json')

