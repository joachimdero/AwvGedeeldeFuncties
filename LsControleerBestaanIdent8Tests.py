import unittest

import requests
from requests import Response

from LsControleerBestaanIdent8 import LsControleerBestaanIdent8
from LsControleerBestaanIdent8Nieuw import LsControleerBestaanIdent8Nieuw, RequestHandler
from LsGetCoordinatesFromIdent8OpschirftAfstandSingle import LsGetCoordinatesFromIdent8OpschirftAfstandSingle


class LsControleerBestaanIdent8Test(unittest.TestCase):
    def test_verifieer_werking(self):
        class Opener():
            def open(self, url):
                cert_path = r'C:\resources\datamanager_eminfra_prd.awv.vlaanderen.be.crt'
                key_path = r'C:\resources\datamanager_eminfra_prd.awv.vlaanderen.be.key'
                proxies = {'https': 'http://proxy.vlaanderen.be:8080/proxy.pac'}
                return OpenerResponse(requests.get(url, cert=(cert_path, key_path)))

        class OpenerResponse:
            def __init__(self, response: Response):
                self.response = response

            def getcode(self):
                return self.response.status_code

            def read(self):
                return self.response.content.decode("utf-8")

        opener = Opener()
        result = LsControleerBestaanIdent8(opener, 'A0120001')
        self.assertEqual('ok', result)

    def test_LsControleerBestaanIdent8Nieuw(self):
        pass
        request_handler = RequestHandler(cert_path = r'/home/davidlinux/Documents/AWV/resources/datamanager_eminfra_prd.awv.vlaanderen.be.crt',
                key_path = r'/home/davidlinux/Documents/AWV/resources/datamanager_eminfra_prd.awv.vlaanderen.be.key')
        result = LsControleerBestaanIdent8Nieuw(request_handler, 'A0120001')
        self.assertEqual('ok', result)

    def test_LsGetCoordinatesFromIdent8OpschirftAfstandSingle(self):
        pass
        request_handler = RequestHandler(cert_path = r'/home/davidlinux/Documents/AWV/resources/datamanager_eminfra_prd.awv.vlaanderen.be.crt',
                key_path = r'/home/davidlinux/Documents/AWV/resources/datamanager_eminfra_prd.awv.vlaanderen.be.key')
        result = LsGetCoordinatesFromIdent8OpschirftAfstandSingle(request_handler, 'A0120001', 19, -50)
        self.assertEqual([147755.9172153825, 193766.7614000047, 0, 18.95], result)


