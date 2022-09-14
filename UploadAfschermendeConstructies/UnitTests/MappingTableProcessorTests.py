from unittest import TestCase
import os

from OTLMOW.OTLModel.Classes.Onderdeel.Geleideconstructie import Geleideconstructie
from OTLMOW.OTLModel.Classes.Onderdeel.Obstakelbeveiliger import Obstakelbeveiliger

from UploadAfschermendeConstructies.EventDataAC import EventDataAC
from UploadAfschermendeConstructies.MappingTableProcessor import MappingTableProcessor

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class MappingTableProcessorTests(TestCase):
    def test_load_mapping_table(self):
        filelocation = os.path.abspath(os.path.join(os.sep, ROOT_DIR, 'test_mapping_tabel.xlsx'))
        processor = MappingTableProcessor(file_path=filelocation)

        self.assertTrue(isinstance(processor.mapping_table, list))
        self.assertGreater(len(processor.mapping_table), 0)

    def test_EventDataAC_DeltaBloc80_output_geleideconstructie(self):
        filelocation = os.path.abspath(os.path.join(os.sep, ROOT_DIR, 'test_mapping_tabel.xlsx'))
        processor = MappingTableProcessor(file_path=filelocation)

        eventDataAC = EventDataAC()
        eventDataAC.product = 'Delta Bloc 80'
        eventDataAC.materiaal = 'beton'

        output = processor.create_otl_objects_from_eventDataAC(eventDataAC)

        self.assertTrue(isinstance(output[0], Geleideconstructie))

    def test_EventDataAC_RimobCrashguard_output_obstakelbeveilger(self):
        filelocation = os.path.abspath(os.path.join(os.sep, ROOT_DIR, 'test_mapping_tabel.xlsx'))
        processor = MappingTableProcessor(file_path=filelocation)

        eventDataAC = EventDataAC()
        eventDataAC.product = 'Rimob Crashguard P800-6S: 0620/3008'
        eventDataAC.materiaal = 'staal'

        output = processor.create_otl_objects_from_eventDataAC(eventDataAC)

        self.assertTrue(isinstance(output[0], Obstakelbeveiliger))
