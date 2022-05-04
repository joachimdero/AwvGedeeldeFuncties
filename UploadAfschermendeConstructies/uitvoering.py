import shapely.wkt
import shapely.ops
from OTLMOW.Facility.DavieExporter import DavieExporter
from OTLMOW.Facility.RequesterFactory import RequesterFactory

from UploadAfschermendeConstructies.FSConnector import FSConnector
from UploadAfschermendeConstructies.JsonToEventDataACProcessor import JsonToEventDataACProcessor
from UploadAfschermendeConstructies.MappingTableProcessor import MappingTableProcessor
from UploadAfschermendeConstructies.OffsetGeometryProcessor import OffsetGeometryProcessor
from UploadAfschermendeConstructies.SettingsManager import SettingsManager

if __name__ == '__main__':
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

    lijst_otl_objecten = []
    mtp = MappingTableProcessor('analyse_afschermende_constructies.xlsx')

    for index, eventDataAC in enumerate(listEventDataAC):
        try:
            otl_object = mtp.create_otl_object_from_eventDataAC(eventDataAC)
            otl_object.assetId.identificator = str(index)
            lijst_otl_objecten.append(otl_object)
        except Exception as e:
            print(e)

    DavieExporter().export_objects_to_json_file(list_of_objects=lijst_otl_objecten, file_path='DAVIE_export_file.json')

    pass
