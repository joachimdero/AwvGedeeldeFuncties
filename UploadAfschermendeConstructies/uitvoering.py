import shapely.wkt
import shapely.ops
from OTLMOW.Facility.DavieExporter import DavieExporter

from UploadAfschermendeConstructies.FSConnector import FSConnector
from UploadAfschermendeConstructies.JsonToEventDataACProcessor import JsonToEventDataACProcessor
from UploadAfschermendeConstructies.MappingTableProcessor import MappingTableProcessor
from UploadAfschermendeConstructies.OffsetGeometryProcessor import OffsetGeometryProcessor

if __name__ == '__main__':
    fs_c = FSConnector()
    raw_output = fs_c.get_raw_lines(layer="afschermendeconstructies",
                                    cert_path=r"C:\GoogleDrive\SyncGisAwv\GIStools\AwvFuncties\Awv\derojp_client.awv.vlaanderen.be.crt",
                                    key_path=r"C:\GoogleDrive\SyncGisAwv\GIStools\AwvFuncties\Awv\derojp_client.awv.vlaanderen.be.key",
                                    lines =20) # beperkt tot 20

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
    for eventDataAC in listEventDataAC:
        otl_object = mtp.create_otl_object_from_eventDataAC(eventDataAC)
        lijst_otl_objecten.append(otl_object)

    DavieExporter().export_objects_to_json_file(list_of_objects=lijst_otl_objecten, file_path='DAVIE_export_file.json')









    pass