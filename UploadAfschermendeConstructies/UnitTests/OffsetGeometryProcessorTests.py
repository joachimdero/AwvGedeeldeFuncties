import unittest

import shapely
from shapely.wkt import loads

from GeometryHelper import GeometryHelper
from UploadAfschermendeConstructies.EventDataAC import EventDataAC
from UploadAfschermendeConstructies.OffsetGeometryProcessor import OffsetGeometryProcessor
from UploadAfschermendeConstructies.OffsetParameters import OffsetParameters
from UploadAfschermendeConstructies.UnitTests.OffsetLineTestData import OffsetLineTestData


class OffsetGeometryProcessorTests(unittest.TestCase):
    def test_create_offset_geometry_from_eventdataAC(self):
        ogp = OffsetGeometryProcessor()
        eventDataAc = EventDataAC()
        eventDataAc.ident8 = 'A0120721'
        eventDataAc.wktLineStringZM = u'LINESTRING M (147620.40680000186 193434.54670000076 0.080000000000000002, 147616.50110000372 193426.20309999958 0.088199999998323619, 147608.74909999967 193411.61510000005 0.10289999999804422, 147600.15110000223 193395.94310000166 0.11879999999655411, 147592.03809999675 193382.0800999999 0.13310000000637956, 147583.80810000002 193369.42410000041 0.14650000000256114, 147577.27210000157 193359.78209999949 0.15690000000176951, 147570.01009999961 193348.69310000166 0.16869999999471474, 147560.81310000271 193335.67709999904 0.18279999999504071, 147550.52610000223 193320.37110000104 0.1992000000027474, 147541.2050999999 193305.78610000014 0.21460000000661239, 147533.5781000033 193293.00809999928 0.22789999999804422, 147527.88509999961 193281.91710000113 0.23889999999664724, 147524.61410000175 193275.76810000092 0.24510000000009313, 147524.17909999937 193274.61410000175 0.24619999999413267, 147523.24109999835 193272.1270999983 0.24860000000626314, 147522.79510000348 193270.94409999996 0.2495000000053551, 147520.85310000181 193265.15509999916 0.25440000000526197, 147520.24210000038 193261.29509999976 0.25750000000698492, 147520.0951000005 193258.39710000157 0.25969999999506399, 147519.99109999835 193256.34710000083 0.26140000000305008, 147520.22609999776 193252.72610000148 0.26420000000507571, 147520.94309999794 193249.10410000011 0.26709999999729916, 147522.66799999774 193244.47679999843 0.27100000000000002)'
        eventDataAc.afstand_rijbaan = 0
        eventDataAc.zijde_rijbaan = 'L'

        outputline = ogp.create_offset_geometry_from_eventdataAC(eventData=eventDataAc)

        expected_result = shapely.wkt.loads(u'LINESTRING M (147621.76532376939 193433.91076511797 0.080000000000000002, 147617.84351907912 193425.53276127018 0.088199999998323619, 147610.06899975229 193410.90238357615 0.10289999999804422, 147601.45619468141 193395.2033976363 0.11879999999655411, 147593.3148586805 193381.29197881371 0.13310000000637956, 147585.05777520503 193368.59433015343 0.14650000000256114, 147578.52041783126 193358.95032772701 0.15690000000176951, 147571.25043722423 193347.84914142825 0.16869999999471474, 147562.04826541041 193334.82582204696 0.18279999999504071, 147551.7807096199 193319.54875303339 0.1992000000027474, 147542.48136746229 193304.99764206074 0.21460000000661239, 147534.89067561107 193292.28047141805 0.22789999999804422, 147529.21454766439 193281.22234125901 0.23889999999664724, 147525.98367655117 193275.14877767023 0.24510000000009313, 147525.58269199813 193274.08501635864 0.24619999999413267, 147524.64459400394 193271.59775646217 0.24860000000626314, 147524.20841937643 193270.44081787951 0.2495000000053551, 147522.3150643043 193264.79682586435 0.25440000000526197, 147521.73613109218 193261.13940819632 0.25750000000698492, 147521.59317397472 193258.32111074124 0.25969999999506399, 147521.49356718123 193256.35770763922 0.26140000000305008, 147521.7165973763 193252.92114449572 0.26420000000507571, 147522.39099148262 193249.51437259559 0.26709999999729916, 147524.07352338624 193245.00073129125 0.27100000000000002)')

        min_buffer_size = GeometryHelper.find_min_buffersize_from_geometry_to_be_within_another(outputline, expected_result)
        self.assertLessEqual(min_buffer_size, 0.10)

    def test_given_input_create_valid_output_with_known_params(self):
        ogp = OffsetGeometryProcessor()

        for t in [(6271, 2, 'right'), (6272, 1.5, 'left'),  (313, 4.5, 'left'), (13858, 4, 'right'), (6276, 1.5, 'left')]:
            with self.subTest(f"testing line {t[0]}"):
                inputline = shapely.wkt.loads(OffsetLineTestData.origineel[t[0]])
                expectedline = shapely.wkt.loads(OffsetLineTestData.offset[t[0]])
                outputline = ogp.apply_offset(geometry=inputline, offset=t[1], side=t[2])

                min_buffer_size = GeometryHelper.find_min_buffersize_from_geometry_to_be_within_another(outputline, expectedline)
                print(f'line {t[0]} has accuracy of {min_buffer_size}')
                self.assertLessEqual(min_buffer_size, 0.10)

    def test_given_eventdataAC_calculate_input_params_zijde_rijbaan(self):
        for t in [('A0120001', 'R', 0, 'right'),
                  ('A0120001', 'L', 0, 'left'),
                  ('A0120002', 'R', 0, 'left'),
                  ('A0120002', 'L', 0, 'right')]:
            with self.subTest(f"testing ident8 {t[0]} zijde {t[1]} afstand {t[2]}"):
                ogp = OffsetGeometryProcessor()
                eventTestData = EventDataAC(ident8=t[0], zijde_rijbaan=t[1], afstand_rijbaan=t[2])
                result = ogp.get_offset_params_from_eventdataAC(eventTestData)

                expected_output = OffsetParameters(zijde=t[3])
                self.assertTrue(isinstance(result, OffsetParameters))
                self.assertEqual(expected_output.zijde, result.zijde)

    def test_given_eventdataAC_calculate_input_params_offset(self):
        for t in [('A0120001', 'R', 1, 5.5),
                  ('A0120001', 'R', -1, 4.5),
                  ('A0120001', 'R', 0, 4.5),
                  ('A0120001', 'L', 0, 4.0),
                  ('N0160001', 'R', 0, 2.0),
                  ('N0160001', 'L', 0, 1.5),
                  ('R0000001', 'R', 0, 4.5),
                  ('R0000001', 'L', 0, 4.0),
                  ('A0120721', 'R', 0, 2.0),
                  ('A0120721', 'L', 0, 1.5),
                  ('N0160121', 'R', 0, 2.0),
                  ('N0160121', 'L', 0, 1.5),
        ]:
            with self.subTest(f"testing ident8 {t[0]} zijde {t[1]} afstand {t[2]}"):
                ogp = OffsetGeometryProcessor()
                eventTestData = EventDataAC(ident8=t[0], zijde_rijbaan=t[1], afstand_rijbaan=t[2])
                result = ogp.get_offset_params_from_eventdataAC(eventTestData)

                expected_output = OffsetParameters(offset=t[3])
                self.assertTrue(isinstance(result, OffsetParameters))
                self.assertEqual(expected_output.offset, result.offset)

