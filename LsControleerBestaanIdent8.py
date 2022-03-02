def LsControleerBestaanIdent8(opener, ident8):
    # controleert of een ident8 bestaat in locatieservices
    import urllib, json
    teller = 0
    status = 'start'
    while status == 'start' and teller < 10:
        try:
            if teller > 0:
                Message = 'poging %s' % teller
                #PrintMessage(Message)
            Leesfunctie = opener.open("https://services.apps.mow.vlaanderen.be/locatieservices/cert/rest/locatie/weg")
            status = str(Leesfunctie.getcode())
            if status == '200':
                status = 'ok'
                LijstIdent8 = json.loads(Leesfunctie.read())  # OK
                if ident8 in LijstIdent8:
                    return 'ok'
                else:
                    return 'ident8 niet in wdb'
            elif status == '404':
                return 'status 404'
        except Exception:
            teller += 1
    if status == 'start':
        return 'error onbekend'