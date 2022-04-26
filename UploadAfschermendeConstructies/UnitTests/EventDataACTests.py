from unittest import TestCase

from UploadAfschermendeConstructies.EventDataAC import EventDataAC
from UploadAfschermendeConstructies.WegLocatieData import WegLocatieData


class EventDataACTests(TestCase):
    def test_init_EventDataAC_without_values_and_assert(self):
        ev = EventDataAC()
        self.assertIsNotNone(ev.ident8)
        self.assertIsNotNone(ev.wktLineStringZM)
        self.assertIsNotNone(ev.begin)
        self.assertIsNotNone(ev.eind)
        self.assertIsNotNone(ev.afstand_rijbaan)
        self.assertIsNotNone(ev.zijde_rijbaan)
        self.assertIsNotNone(ev.typeAC)
        self.assertIsNotNone(ev.product)
        self.assertTrue(isinstance(ev.begin, WegLocatieData))
        self.assertTrue(isinstance(ev.eind, WegLocatieData))
        self.assertTrue(isinstance(ev.afstand_rijbaan, float))
        self.assertTrue(isinstance(ev.zijde_rijbaan, str))

    def test_init_EventDataAC_with_values_and_assert(self):
        ev = EventDataAC()
        ev.ident8 = 'A0120001'
        ev.wktLineStringZM = "LINESTRING ZM (204687.014412866 207284.945373632 0 23.331, 204687.998785856 207284.800409002 0 23.332)"
        ev.tt = "e"
        ev.ident8 = 0

        self.assertEqual('A0120001', ev.ident8)
        self.assertEqual("LINESTRING ZM (204687.014412866 207284.945373632 0 23.331, 204687.998785856 207284.800409002 0 23.332)", ev.wktLineStringZM)

