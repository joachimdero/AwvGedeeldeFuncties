import shapely
import shapely.ops
from shapely.wkt import loads
from shapely.geometry import LineString, Point
from shapely.geometry.base import BaseGeometry

from UploadAfschermendeConstructies.EventDataAC import EventDataAC
from UploadAfschermendeConstructies.EventRijbaan import EventRijbaan
from UploadAfschermendeConstructies.OffsetParameters import OffsetParameters


class OffsetGeometryProcessor:
    def create_offset_geometry_from_eventdataAC(self, eventData: EventDataAC, round_precision: int = -1) -> BaseGeometry:
        params = self.get_offset_params_from_eventdataAC(eventData)
        input_geom = shapely.wkt.loads(eventData.wktLineStringZ)
        if input_geom.length == 0:
            # is a point, not a line
            eventData.needs_offset = True
            return input_geom
        else:
            try:
                geom = self.apply_offset(geometry=input_geom, offset=params.offset, side=params.zijde)
                eventData.needs_offset = False

                if round_precision != -1:
                    new_wkt = shapely.wkt.dumps(geom, rounding_precision=round_precision)
                    shape = shapely.wkt.loads(new_wkt)
                    new_shape = shapely.ops.transform(lambda x, y: (x, y, 0), shape)
                    new_wkt = new_shape.wkt
                    geom = shapely.wkt.loads(new_wkt)
            except Exception as e:
                print(e)
                eventData.needs_offset = True

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

        is_hoofdweg = ((wegtype in ['A', 'B'] or eventData.ident8.startswith('R00')) and eventData.ident8[4:7] == '000')
        is_af_oprit_hoofdweg = ((wegtype == 'A' or eventData.ident8.startswith('R00')) and eventData.ident8[4:7] != '000')
        is_n_weg = (wegtype == 'N' or wegtype == 'T' or (eventData.ident8.startswith('R') and not eventData.ident8.startswith('R00')))
        is_zijde_rijbaan_R = (eventData.zijde_rijbaan == 'R')
        is_zijde_rijbaan_L = (eventData.zijde_rijbaan == 'L')

        if not is_hoofdweg and not is_af_oprit_hoofdweg and not is_n_weg:
            pass

        mappingtabel = {
            (1, 0, 0, 1, 0): 4.5,
            (1, 0, 0, 0, 1): 4.0,
            (0, 1, 0, 1, 0): 2.0,
            (0, 1, 0, 0, 1): 1.5,
            (0, 0, 1, 1, 0): 2.0,
            (0, 0, 1, 0, 1): 1.5,
        }
        try:
            offset = mappingtabel[(is_hoofdweg, is_af_oprit_hoofdweg, is_n_weg, is_zijde_rijbaan_R, is_zijde_rijbaan_L)]
            return eventData.afstand_rijbaan + offset
        except Exception as e:
            print(f'missing mapping for determine_offset, id {eventData.id}: (is_hoofdweg={is_hoofdweg}, '
                  f'is_af_oprit_hoofdweg={is_af_oprit_hoofdweg}, is_n_weg={is_n_weg}, is_zijde_rijbaan_R={is_zijde_rijbaan_R}, '
                  f'is_zijde_rijbaan_L={is_zijde_rijbaan_L})')

        return eventData.afstand_rijbaan


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

        if eventData.zijde_rijbaan == 'M':
            raise NotImplementedError('zijde rijbaan == M ==> object wordt niet gemapt')

        try:
            return mappingtabel[(is_zijde_rijbaan_R, is_zijde_rijbaan_L, is_wegnr_1, is_wegnr_2)]
        except Exception as e:
            print(f'missing mapping for determine_zijde, id {eventData.id}: (is_zijde_rijbaan_R={is_zijde_rijbaan_R}, '
                  f'is_zijde_rijbaan_L={is_zijde_rijbaan_L}, is_wegnr_1={is_wegnr_1}, is_wegnr_2={is_wegnr_2})')

        return None

    def process_wkt_to_Z(self, eventDataAC):
        wktString = eventDataAC.wktLineStringZM
        shape = shapely.wkt.loads(wktString)
        new_shape = shapely.ops.transform(lambda x, y, z: (x, y, z), shape)
        new_wkt = new_shape.wkt
        eventDataAC.wktLineStringZ = new_wkt

    def try_fixing_points_via_relations(self, eventDataAC):
        valid_candidates = []
        eventDataAC.shape = Point(eventDataAC.shape.coords[0])
        for candidate in eventDataAC.candidates:
            intersected_geometry = eventDataAC.shape.intersection(candidate.shape)

            if intersected_geometry.is_empty:
                continue

            if isinstance(intersected_geometry, Point):
                valid_candidates.append(candidate)

        if len(valid_candidates) != 1:
            return

        valid_candidate = valid_candidates[0]
        if not hasattr(valid_candidate, 'offset_geometry'):
            return

        start = valid_candidate.shape.coords[0]
        end = valid_candidate.shape.coords[-1]
        if start == eventDataAC.shape.coords[0]:
            new_start = valid_candidate.offset_geometry.coords[0]
            eventDataAC.offset_geometry = LineString([new_start, new_start])
            eventDataAC.offset_wkt = eventDataAC.offset_geometry.wkt
            eventDataAC.needs_offset = False
        elif end == eventDataAC.shape.coords[0]:
            new_end = valid_candidate.offset_geometry.coords[-1]
            eventDataAC.offset_geometry = LineString([new_end, new_end])
            eventDataAC.offset_wkt = eventDataAC.offset_geometry.wkt
            eventDataAC.needs_offset = False

    def add_rijstrook_info_to_event_data_ac(self, list_event_data_ac: [EventDataAC], list_rijbanen: [EventRijbaan]):
        for event_ac in list_event_data_ac:
            rijbanen = list(filter(lambda r: r.ident8 == event_ac.ident8, list_rijbanen))
            if len(rijbanen) == 0:
                continue
            begin_rijbaan = list(filter(lambda r: r.begin.positie <= event_ac.begin.positie <= r.eind.positie, rijbanen))
            midden_rijbaan = list(filter(lambda r: event_ac.begin.positie <= r.begin.positie <= r.eind.positie <= event_ac.eind.positie, rijbanen))
            eind_rijbaan = list(filter(lambda r: r.begin.positie <= event_ac.eind.positie <= r.eind.positie, rijbanen))
            if len(begin_rijbaan) + len(midden_rijbaan) + len(eind_rijbaan) == 0:
                continue

            rijbanen_dict = {}
            for r in begin_rijbaan:
                rijbanen_dict[r.id] = r
            for r in midden_rijbaan:
                rijbanen_dict[r.id] = r
            for r in eind_rijbaan:
                rijbanen_dict[r.id] = r

            if len(rijbanen_dict.values()) == 1:
                rijbaan_to_use = list(rijbanen_dict.values())[0]
                if rijbaan_to_use.breedte_rijbaan is not None:
                    event_ac.breedte_rijbaan = rijbaan_to_use.breedte_rijbaan
                else:
                    event_ac.breedte_rijbaan = (rijbaan_to_use.aantal_rijstroken, rijbaan_to_use.wegcategorie)

                print(f'event ac {event_ac.id} now has breedte_rijbaan: {event_ac.breedte_rijbaan}')
            else:
                calc_breedte = 0.0
                lengte = event_ac.eind.positie - event_ac.begin.positie
                used_lengte = 0.0
                for rijbaan_to_use in rijbanen_dict.values():

                    if rijbaan_to_use.breedte_rijbaan is None:
                        rijbaan_to_use.breedte_rijbaan = 600  # TODO needs to come from mapping

                    print(f'using rijbaan with width {rijbaan_to_use.breedte_rijbaan} and length {round(rijbaan_to_use.eind.positie - rijbaan_to_use.begin.positie, 3)}')

                    if rijbaan_to_use.begin.positie <= event_ac.begin.positie:
                        calc_breedte += rijbaan_to_use.breedte_rijbaan * (rijbaan_to_use.eind.positie - event_ac.begin.positie)
                        used_lengte += rijbaan_to_use.eind.positie - event_ac.begin.positie
                    elif rijbaan_to_use.eind.positie >= event_ac.eind.positie:
                        calc_breedte += rijbaan_to_use.breedte_rijbaan * (event_ac.eind.positie - rijbaan_to_use.begin.positie)
                        used_lengte += event_ac.eind.positie - rijbaan_to_use.begin.positie
                    else:
                        calc_breedte += rijbaan_to_use.breedte_rijbaan * (rijbaan_to_use.eind.positie - rijbaan_to_use.begin.positie)
                        used_lengte += rijbaan_to_use.eind.positie - rijbaan_to_use.begin.positie

                if used_lengte < lengte:
                    calc_breedte = int(calc_breedte / used_lengte)  # TODO OK? or have a %?
                else:
                    calc_breedte = int(calc_breedte / lengte)
                print(f'calculated result breedte_rijbaan: {calc_breedte}')
                pass