import unittest

from UploadAfschermendeConstructies.EventDataAC import EventDataAC
from UploadAfschermendeConstructies.FSConnector import FSConnector
from UploadAfschermendeConstructies.JsonToEventDataACProcessor import JsonToEventDataACProcessor


class FSConnectorTests(unittest.TestCase):
    def test_load_10_afschermende_constructies(self):
        fs_c = FSConnector()
        raw_output = fs_c.get_raw_lines(layer="afschermendeconstructies", lines=20,
                                        cert_path = r'C:\resources\datamanager_eminfra_prd.awv.vlaanderen.be.crt',
                                        key_path = r'C:\resources\datamanager_eminfra_prd.awv.vlaanderen.be.key')

        self.assertEqual(20, len(raw_output))

    def test_load_10_afschermende_constructies_and_process(self):
        fs_c = FSConnector()
        raw_output = fs_c.get_raw_lines(layer="afschermendeconstructies",  lines=20,
                                        cert_path = r'C:\resources\datamanager_eminfra_prd.awv.vlaanderen.be.crt',
                                        key_path = r'C:\resources\datamanager_eminfra_prd.awv.vlaanderen.be.key')
        processed_output = JsonToEventDataACProcessor().processJson(raw_output)

        self.assertEqual(20, len(processed_output))
        self.assertTrue(isinstance(processed_output[0], EventDataAC))
