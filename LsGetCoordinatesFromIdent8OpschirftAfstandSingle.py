import json


def LsGetCoordinatesFromIdent8OpschirftAfstandSingle(request_handler, ident8, opschrift, afstand, retries=10):
    """vraag positie, paal en afstand op, op basis van coordinaten"""

    ident8 = ident8.strip()

    status = None
    for attempt in range(retries):
        if attempt > 0:
            Message = f'poging {attempt}'
            # PrintMessage(Message)
        try:
            url = f'https://services.apps.mow.vlaanderen.be/locatieservices/cert/rest/locatie/weglocatie?ident8={ident8}' \
                  f'&opschrift={opschrift}&afstand={afstand}&bronCrs=31370&doelCrs=31370'
            response = request_handler.perform_get_request(url)
            status = response.status_code

            if status == 404:
                return 'status 404'

            elif status == 200:
                locaties = json.loads(request_handler.get_content())
                return locaties['geometry']['coordinates']
        except Exception as ex:
            print(str(ex))
    if status is None:
        return 'error onbekend'