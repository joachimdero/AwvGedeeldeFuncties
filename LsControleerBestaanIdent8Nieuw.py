import json
import os

import requests


class RequestHandler:
    # config ini
    # verschillende omgevingen
    def __init__(self, cert_path: str, key_path: str):
        if not os.path.isfile(cert_path):
            raise FileNotFoundError('certificate file not found')
        if not os.path.isfile(key_path):
            raise FileNotFoundError('key file not found')
        self.cert_path = cert_path
        self.key_path = key_path
        self.proxies = {'https': 'http://proxy.vlaanderen.be:8080/proxy.pac'}

    def perform_get_request(self, url, use_proxies=False):
        if not use_proxies:
            self.proxies = None
        self.response = requests.get(url=url,
                                     cert=(self.cert_path, self.key_path),
                                     proxies=self.proxies)
        return self.response

    def get_content(self):
        return self.response.content.decode("utf-8")


def LsControleerBestaanIdent8Nieuw(request_handler, ident8, retries=10):
    """Controleert of een ident8 bestaat in locatieservices"""

    for attempt in range(retries):
        if attempt > 0:
            Message = f'poging {attempt}'
            # PrintMessage(Message)
        try:
            response = request_handler.perform_get_request('https://services.apps.mow.vlaanderen.be/locatieservices/cert/rest/locatie/weg')
            status = response.status_code

            if status == 404:
                return 'status 404'

            elif status == 200:
                LijstIdent8 = json.loads(request_handler.get_content())
                if ident8 in LijstIdent8:
                    return 'ok'
                else:
                    return 'ident8 niet in wdb'
        except Exception as ex:
            print(str(ex))
    if status is None:
        return 'error onbekend'
