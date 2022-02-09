import shapely.wkt
import shapely.ops
from UploadAfschermendeConstructies.FSConnector import FSConnector
from UploadAfschermendeConstructies.JsonToEventDataACProcessor import JsonToEventDataACProcessor
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
    for eventDataAC in listEventDataAC :
        wktString = eventDataAC.wktLineStringZM
        shape = shapely.wkt.loads(wktString)
        new_shape = shapely.ops.transform(lambda x, y, z: (x, y, z), shape)
        new_wkt = new_shape.wkt
        eventDataAC.wktLineStringZM = new_wkt








    pass