import json
import os
from unittest import TestCase

from UploadAfschermendeConstructies.JsonToEventDataACProcessor import JsonToEventDataACProcessor

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class BeginEnEindProcessorTests(TestCase):
    def test_load_json(self):
        processor = JsonToEventDataACProcessor()

        filelocation = os.path.abspath(os.path.join(os.sep, ROOT_DIR, 'beginEnEindConstructies.json'))

        with open(filelocation) as datafile:
            jsonData = json.load(datafile)
        listEventDataAC = processor.process_json_object_or_list_ac(jsonData, is_list=True)

        self.assertGreater(len(listEventDataAC), 0)
