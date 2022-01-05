import unittest

from GeometryHelper import GeometryHelper


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
