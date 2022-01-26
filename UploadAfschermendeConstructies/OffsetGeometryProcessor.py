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
        if (wegtype == 'A' or eventData.ident8.startswith('R00')) and eventData.ident8[4:7] == '000':
            if eventData.zijde_rijbaan == 'R':
                return eventData.afstand_rijbaan + 4.5
            elif eventData.zijde_rijbaan == 'L':
                return eventData.afstand_rijbaan + 4.0
        elif (wegtype == 'A' or eventData.ident8.startswith('R00')) and eventData.ident8[4:7] != '000':
            if eventData.zijde_rijbaan == 'R':
                return eventData.afstand_rijbaan + 2.0
            elif eventData.zijde_rijbaan == 'L':
                return eventData.afstand_rijbaan + 1.5
        elif wegtype == 'N':
            if eventData.zijde_rijbaan == 'R':
                return eventData.afstand_rijbaan + 2.0
            elif eventData.zijde_rijbaan == 'L':
                return eventData.afstand_rijbaan + 1.5

    def determine_zijde(self, eventData):
        wegnr = eventData.ident8[-1]
        if eventData.zijde_rijbaan == 'R':
            if wegnr == '1':
                return 'right'
            elif wegnr == '2':
                return 'left'
        elif eventData.zijde_rijbaan == 'L':
            if wegnr == '1':
                return 'left'
            elif wegnr == '2':
                return 'right'