import json
import unittest
from math import sqrt

import numpy as np
import shapely.wkt
import shapely.geometry
from shapely.geometry import shape, mapping

from GeometryHelper import GeometryHelper
from UploadAfschermendeConstructies.UnitTests.OffsetLineTestData import OffsetLineTestData


class GeometryHelperTest(unittest.TestCase):
    def test_0_0_uitkomst_0(self):
        # arrange = klaarzetten voorbereiden
        a = 0.0
        b = 0.0

        # act: effectief uitvoeren
        resultaat = GeometryHelper.bereken_hoek(a, b)

        # assert: controle tussen resultaat en verwacht
        verwacht = 0.0
        self.assertEqual(verwacht, resultaat)

    def test_0_1_uitkomst_1(self):
        # arrange = klaarzetten voorbereiden
        a = 0.0
        b = 1.0

        # act: effectief uitvoeren
        resultaat = GeometryHelper.bereken_hoek(a, b)

        # assert: controle tussen resultaat en verwacht
        verwacht = 1.0
        self.assertEqual(verwacht, resultaat)

    def test_1_1_uitkomst_0(self):
        # arrange = klaarzetten voorbereiden
        a = 1.0
        b = 1.0

        # act: effectief uitvoeren
        resultaat = GeometryHelper.bereken_hoek(a, b)

        # assert: controle tussen resultaat en verwacht
        verwacht = 0.0
        self.assertEqual(verwacht, resultaat)

    def test_0_181_uitkomst_min179(self):
        # arrange = klaarzetten voorbereiden
        a = 0
        b = 181

        # act: effectief uitvoeren
        resultaat = GeometryHelper.bereken_hoek(a, b)

        # assert: controle tussen resultaat en verwacht
        verwacht = -179
        self.assertEqual(verwacht, resultaat)

    def test_0_800_uitkomst_80(self):
        # arrange = klaarzetten voorbereiden
        a = 0
        b = 800

        # act: effectief uitvoeren
        resultaat = GeometryHelper.bereken_hoek(a, b)

        # assert: controle tussen resultaat en verwacht
        verwacht = 80
        self.assertEqual(verwacht, resultaat)

    def test_0_min800_uitkomst_min80(self):
        # arrange = klaarzetten voorbereiden
        a = 0
        b = -800

        # act: effectief uitvoeren
        resultaat = GeometryHelper.bereken_hoek(a, b)

        # assert: controle tussen resultaat en verwacht
        verwacht = -80
        self.assertEqual(verwacht, resultaat)

    def test_0_str180_uitkomst_typeError(self):
        # arrange = klaarzetten voorbereiden
        a = 0
        b = "180"

        # act: effectief uitvoeren

        # assert: controle tussen resultaat en verwacht
        with self.assertRaises(TypeError):
            resultaat = GeometryHelper.bereken_hoek(a, b)

    def test_0_None_uitkomst_valueError(self):
        # arrange = klaarzetten voorbereiden
        a = 0
        b = None

        # act: effectief uitvoeren

        # assert: controle tussen resultaat en verwacht
        with self.assertRaises(ValueError) as NoneValueError:
            resultaat = GeometryHelper.bereken_hoek(a, b)
        self.assertEqual(str(NoneValueError.exception), "None is geen geldige waarde")

    def test_find_min_buffersize_from_geometry_to_be_within_another(self):
        line = shapely.wkt.loads(
            'LINESTRING ZM (161468.378768416 160252.040726318 0 12.054, 161473.488399997 160248.7412 0 12.0601500000048, '
            '161485.656400003 160239.505199999 0 12.0755499999941, 161497.47762291 160231.46343517 0 12.09)')
        translated_line = line.parallel_offset(distance=4, side='right', join_style=3)

        result = GeometryHelper.find_min_buffersize_from_geometry_to_be_within_another(geometry=line,
                                                                                       within_geometry=translated_line)
        self.assertEqual(4.00577, result)

    def test_find_min_buffersize_from_geometry_to_be_within_another_fixed_example(self):
        line = shapely.wkt.loads('LINESTRING (0 0, 0 1, 1 1)')
        new_line = shapely.wkt.loads('LINESTRING (0 0, 1 1)')

        result = GeometryHelper.find_min_buffersize_from_geometry_to_be_within_another(geometry=line, within_geometry=new_line)
        self.assertEqual(round(sqrt(2) / 2, 5), result)

    def test_round_wkt(self):
        g1 = shapely.wkt.loads(OffsetLineTestData.origineel[6273])
        g2 = shape(g1)
        geojson = mapping(g2)
        geojson['coordinates'] = np.round(np.array(geojson['coordinates']), 3)
        g2 = shape(geojson)
        print(g2.wkt)

