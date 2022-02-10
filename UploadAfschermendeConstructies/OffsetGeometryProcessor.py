import shapely
from shapely.wkt import loads
from shapely.geometry import LineString
from shapely.geometry.base import BaseGeometry

from UploadAfschermendeConstructies.EventDataAC import EventDataAC
from UploadAfschermendeConstructies.OffsetParameters import OffsetParameters


class OffsetGeometryProcessor:
    def create_offset_geometry_from_eventdataAC(self, eventData: EventDataAC) -> BaseGeometry:
        params = self.get_offset_params_from_eventdataAC(eventData)
        input_geom = shapely.wkt.loads(eventData.wktLineStringZM)
        geom = self.apply_offset(geometry=input_geom, offset=params.offset, side=params.zijde)
        return geom

    def apply_offset(self, geometry, offset, side):
        return geometry.parallel_offset(distance=offset, side=side, join_style=2)

    def get_offset_params_from_eventdataAC(self, eventData: EventDataAC):
        return OffsetParameters(
            zijde=self.determine_zijde(eventData),
            offset=self.determine_offset(eventData))

    def determine_offset(self, eventData):
        if eventData.afstand_rijbaan == -1:
            eventData.afstand_rijbaan = 0
        wegtype = eventData.ident8[0]

        is_hoofdweg = ((wegtype == 'A' or eventData.ident8.startswith('R00')) and eventData.ident8[4:7] == '000')
        is_af_oprit_hoofdweg = ((wegtype == 'A' or eventData.ident8.startswith('R00')) and eventData.ident8[4:7] != '000')
        is_n_weg = (wegtype == 'N')
        is_zijde_rijbaan_R = (eventData.zijde_rijbaan == 'R')
        is_zijde_rijbaan_L = (eventData.zijde_rijbaan == 'L')

        mappingtabel = {
            (1, 0, 0, 1, 0): 4.5,
            (1, 0, 0, 0, 1): 4.0,
            (0, 1, 0, 1, 0): 2.0,
            (0, 1, 0, 0, 1): 1.5,
            (0, 0, 1, 1, 0): 2.0,
            (0, 0, 1, 0, 1): 1.5,
        }

        return eventData.afstand_rijbaan + mappingtabel[(is_hoofdweg, is_af_oprit_hoofdweg, is_n_weg, is_zijde_rijbaan_R, is_zijde_rijbaan_L)]


    def determine_zijde(self, eventData):
        wegnr = eventData.ident8[-1]

        is_zijde_rijbaan_R = (eventData.zijde_rijbaan == 'R')
        is_zijde_rijbaan_L = (eventData.zijde_rijbaan == 'L')
        is_wegnr_1 = (wegnr == '1')
        is_wegnr_2 = (wegnr == '2')

        mappingtabel = {
            (1, 0, 1, 0): 'right',
            (1, 0, 0, 1): 'left',
            (0, 1, 1, 0): 'left',
            (0, 1, 0, 1): 'right',
        }

        return mappingtabel[(is_zijde_rijbaan_R, is_zijde_rijbaan_L, is_wegnr_1, is_wegnr_2)]
