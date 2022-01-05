import unittest

from GeometryHelper import GeometryHelper


def berekenHoek(bearing1, bearing2):
    """bereken de hoek tussen 2 lijnen met als bron 'bearing' van de lijn"""
    g = GeometryHelper()
    return g.bereken_hoek(bearing1, bearing2)


class BerekenHoekFunctieTests(unittest.TestCase):
    def test_0_10_uitkomst_10(self):
        # arrange = klaarzetten voorbereiden
        a = 0.0
        b = 10.0

        # act: effectief uitvoeren
        resultaat = berekenHoek(a, b)

        # assert: controle tussen resultaat en verwacht
        verwacht = 10.0
        self.assertEqual(verwacht, resultaat)

    def test_min100_100_uitkomst_min160(self):
        # arrange = klaarzetten voorbereiden
        a = -100.0
        b = 100.0

        # act: effectief uitvoeren
        resultaat = berekenHoek(a, b)

        # assert: controle tussen resultaat en verwacht
        verwacht = -160.0
        self.assertEqual(verwacht, resultaat)


print(berekenHoek(0, 10))
