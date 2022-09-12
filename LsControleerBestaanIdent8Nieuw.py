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



def LsGetRelatieveWegLocatieFromXYSingle(x,y,opener):
##    Message = 'Locaties:%s' %Locaties;PrintMessage(Message)
    # vraag positie, paal en afstand op, op basis van coordinaten
    # legacy true = maak gebruik van relatieve hmlocaties indien er geen palen zijn
    # benader true =  snap naar eindpunten indien de locatie niet loodrecht geprojecteerd kan worden op de route

    import json,urllib2
    #vraag locatie op
    teller = 0 # teller telt aantal pogingen tot opvragen van de positie
    status = -1 # default waarde
#https://apps.mow.vlaanderen.be/locatieservices/rest/locatie/weglocatie/relatief/via/xy?y=166734.290&x=137608.885&bronCrs=31370&doelCrs=31370


    Url = "https://services.apps.mow.vlaanderen.be/locatieservices/cert/rest/locatie/weglocatie/via/xy?x=%s&y=%s&bronCrs=31370&doelCrs=31370" % (x,y)
    print (Url)

    status = -1 # default waarde

    while status not in (200,404) and teller < 10:# probeer meerdere malen indien  ls niet reageerd
##                PrintMessage('voer request uit')

        if teller > 0:
            Message = 'poging %s' %teller
##            PrintMessage(Message)

        # voer request uit
##        PrintMessage('voer request uit')
        req = urllib2.Request(Url, headers={"Content-Type": "application/vnd.awv.wdb-v3.0+json"})
        print (str(req))
##                req = urllib2.Request("https://services.apps.mow.vlaanderen.be/locatieservices/cert/rest/weglocatie/")


        Leesfunctie = opener.open(req)
        status = (Leesfunctie.getcode())
##                PrintMessage(('status:',str(status)))
        if status == 200:
##            PrintMessage("status ok")
            OpgevraagdeLocaties = json.loads(Leesfunctie.read())  # OK

            Ident8 = OpgevraagdeLocaties["ident8"]
            Positie = OpgevraagdeLocaties["positie"]
            Opschrift = OpgevraagdeLocaties["opschrift"]
            Afstand = OpgevraagdeLocaties["afstand"]


    return OpgevraagdeLocaties