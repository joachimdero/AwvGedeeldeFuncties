from unittest import TestCase

from OTLMOW.OTLModel.Classes.Geleideconstructie import Geleideconstructie
from OTLMOW.OTLModel.Classes.GetesteBeginconstructie import GetesteBeginconstructie

from UploadAfschermendeConstructies.DataToAssetProcessor import DataToAssetProcessor
from UploadAfschermendeConstructies.EventDataAC import EventDataAC

class DataToAssetProcessorTests(TestCase):
    def test_empty_EventDataAC_with_geometry(self):
        input = EventDataAC()
        input.wktLineStringZM = 'LINESTRING Z (0 1 2, 3 4 5)'
        processor = DataToAssetProcessor()

        output = processor.process_eventDataAC_to_assets(input)

        self.assertEqual(Geleideconstructie.typeURI, output[0].typeURI)
        self.assertEqual(input.wktLineStringZM, output[0].geometry)

    def test_EventDataAC_type_begin_eind_product_contains_eind(self):
        processor = DataToAssetProcessor()
        input = EventDataAC()
        input.wktLineStringZM = 'LINESTRING Z (0 1 2, 3 4 5)'

        with self.subTest('product = Beginconstructie SafeEnd P4 - terminal'):

            input.typeAC = 'begin- en eindconstructie'
            input.product = 'Beginconstructie SafeEnd P4 - terminal'

            output = processor.process_eventDataAC_to_assets(input)
            self.assertEqual(GetesteBeginconstructie.typeURI, output[0].typeURI)
            self.assertEqual('SafeEnd P4 - terminal', output[0].productnaam)
            self.assertEqual('https://www.saferoad.nl/contentassets/eb7874415681447eb4f6a869011d5099/working-instruction---safeend-p4.pdf', output[0].productidentificatiecode.linkTechnischeFiche)
            self.assertEqual('Saferoad Holland BV', output[0].productidentificatiecode.producent)
