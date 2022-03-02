# verzameling van AWVfuncties
# voeg op volgende manier toe aan  andere scripts
'''
#check pythonversie
import sys,os
pythonVersion = sys.version_info.major

#importeer Awv functie en downloadFunctie
from sys import path
basispath =  os.path.realpath(__file__).split("awvDataTools")[0]
print ("basispath = ",basispath)
path2 =  os.path.join(basispath,"awvDataTools", "AwvFuncties")
path.append(path2)
import AwvFuncties
import downloadGeolatteNoSqlFuncties

if pythonVersion == 3:
    importlib.reload(AwvFuncties)
    importlib.reload(downloadGeolatteNoSqlFuncties)
    arcpy.AddMessage("reload python 3")
elif pythonVersion == 2:
    reload (AwvFuncties)
    reload (downloadGeolatteNoSqlFuncties)
    arcpy.AddMessage("reload python 2")

'''

'''
#importeer wegenregister functie
import os, importlib, arcpy
basispath =  os.path.realpath(__file__).split("GIStools")[0]
arcpy.AddMessage( "basispath = %s" % basispath )
path2 =  os.path.join(basispath,"GIStools", "AwvFuncties")
from sys import path
path.append(path2)
import Wegenregister2
try:
    importlib.reload(Wegenregister2)
    arcpy.AddMessage("reload python 3")
except:
    reload (Wegenregister2)
    arcpy.AddMessage("reload python 2")
'''


def CertificaatPython3(Omgeving):
    import http.client, os, arcpy
    arcpy.AddMessage("maak opener voor python 3")
    from urllib.request import HTTPSHandler, ProxyHandler, build_opener
    ##    class HTTPSClientAuthHandler(urllib2.HTTPSHandler):

    class HTTPSClientAuthHandler(HTTPSHandler):
        def __init__(self, key, cert):
            ##            urllib2.HTTPSHandler.__init__(self)
            HTTPSHandler.__init__(self)
            self.key = key
            self.cert = cert

        def https_open(self, req):
            return self.do_open(self.getConnection, req)

        def getConnection(self, host, timeout=300):
            return http.client.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)

    if Omgeving not in ('productie', 'tei', 'dev'):
        PrintMessage('Omgeving niet correct')
    else:
        Message = 'Omgeving = %s' % Omgeving;PrintMessage(Message)

    basispath = os.path.realpath(__file__).split("GIStools")[0]
    path2 = os.path.join(basispath, "GIStools", "AwvFuncties")

    KeyWdb = os.path.join(path2, r"Awv\derojp_client.awv.vlaanderen.be.key")
    CrtWdb = os.path.join(path2, r"Awv\derojp_client.awv.vlaanderen.be.crt")

    proxy_handler = ProxyHandler({'https': 'http://proxy.vlaanderen.be:8080/proxy.pac'})

    ##    arcpy.AddMessage(KeyWdb)
    opener = build_opener(proxy_handler, HTTPSClientAuthHandler(KeyWdb, CrtWdb))
    # test
    try:
        opener.open("https://www.google.com")
        PrintMessage('met proxy')
    except:
        proxy_handler = ProxyHandler(None)
        opener = build_opener(proxy_handler, HTTPSClientAuthHandler(KeyWdb, CrtWdb))
        opener.open("https://www.google.com")
        PrintMessage('zonder proxy')

    return opener


def Certificaat(Omgeving):
    import urllib2, httplib, os
    class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
        def __init__(self, key, cert):
            urllib2.HTTPSHandler.__init__(self)
            self.key = key
            self.cert = cert

        def https_open(self, req):
            return self.do_open(self.getConnection, req)

        def getConnection(self, host, timeout=300):
            return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)

    if Omgeving not in ('productie', 'tei', 'dev'):
        PrintMessage('Omgeving niet correct')
    else:
        Message = 'Omgeving = %s' % Omgeving;PrintMessage(Message)

    try:
        basispath = os.path.realpath(__file__).split("GIStools")[0]
    except:
        basispath = r"C:\GoogleDrive\SyncGisAwv"
    path2 = os.path.join(basispath, "GIStools", "AwvFuncties")

    KeyWdb = os.path.join(path2, r"Awv\derojp_client.awv.vlaanderen.be.key")
    CrtWdb = os.path.join(path2, r"Awv\derojp_client.awv.vlaanderen.be.crt")

    ##    proxy_handler = urllib2.ProxyHandler({'https': 'http://proxy.vlaanderen.be:8080'})
    ##    proxy_handler = urllib2.ProxyHandler(None)
    proxy_handler = urllib2.ProxyHandler({'https': 'http://proxy.vlaanderen.be:8080/proxy.pac'})

    opener = urllib2.build_opener(proxy_handler, HTTPSClientAuthHandler(KeyWdb, CrtWdb))
    # test
    try:
        opener.open("https://www.google.com")
        PrintMessage('met proxy')
    except:
        proxy_handler = urllib2.ProxyHandler(None)
        ##        proxy_handler = urllib2.ProxyHandler({'https': 'http://proxy.vlaanderen.be:8080'})
        opener = urllib2.build_opener(proxy_handler, HTTPSClientAuthHandler(KeyWdb, CrtWdb))
        opener.open("https://www.google.com")
        PrintMessage('zonder proxy')

    ##    opener = urllib2.build_opener(HTTPSClientAuthHandler(KeyWdb, CrtWdb))

    ##    #test
    ##    opener.open("https://www.google.com")

    return opener


"""
Prepareert een sessie (authenticatie)

Geef ofwel een cookie op, ofwel de een tuple van (key-file-path, cert-file-path).
Opm: Proxies moeten met environment variables gezet worden

"""


def prepare_session(cookie=None, cert=None):
    import requests
    print("prepare_session")
    print("cookie = %s, cert = %s" % (cookie, cert))
    s = requests.Session()
    if cookie is not None:
        s.headers.update({'Cookie': 'acm-awv={}'.format(cookie),
                          'Content-type': 'application/json'
                          })
        print("updated cookie")
    if cert is not None:
        s.cert = cert
    print("s=%s" % s)
    return s


def PrintMessage(Message):
    # print message zowel in pyscripter,... als arcgis
    from arcpy import AddMessage
    if type(Message) in (tuple, list):
        ##        print 'list'
        Message = ' '.join(str(x) for x in Message)
    try:
        print(Message)
        AddMessage(Message)
    except:
        print("print niet mogelijk")

# TODO validate
def PrintLogMessage(Message, LogfilePath):
    # print message zowel in pyscripter,... als arcgis en schrijf deze ook naar een log file
    PrintMessage(Message)
    with open(LogfilePath, 'a') as Logfile:
        Logfile.writelines(Message + '\n')


def PrintLogMessage(Message, LogfilePath):
    # print message zowel in pyscripter,... als arcgis en schrijf deze ook naar een log file
    from arcpy import AddMessage
    if type(Message) in (tuple, list):
        ##        print 'list'
        Message = ' '.join(Message)
    print(Message)
    AddMessage(Message)
    Logfile = open(LogfilePath, 'a')
    Logfile.writelines(Message + '\n')
    Logfile.close()

# TODO validate
def LogMessage(Message, LogfilePath):
    # print message zowel in pyscripter,... als arcgis en schrijf deze ook naar een log file
    if type(Message) in (tuple, list):
        ##        print 'list'
        Message = ' '.join(Message)
    with open(LogfilePath, 'a') as Logfile:
        Logfile.writelines(Message + '\n')


def MaakTawVeldTawVanGebied(InputTable, Gebied):
    from arcpy import AddField_management
    from arcpy.da import UpdateCursor
    from arcpy import AddMessage, AddWarning, AddError
    PrintMessage("\n MaakTawVeldTawVanGebied(%s,%s)" % (InputTable, Gebied))
    # bereken territoriale afdeling uit gebied (district)
    PrintMessage("maak veld 'taw' (territoriale afdeling wegen) en bereken")
    AddField_management(InputTable, "taw", "TEXT", "#", "#", 50)  # maak veld 'lengte' aan

    AfdelingGebied = {
        'Antwerpen': range(100, 130),
        'Vlaams-Brabant': range(200, 230),
        'Oost-Vlaanderen': range(400, 430),
        'West-Vlaanderen': range(300, 330),
        'Limburg': range(700, 730),
    }

    with UpdateCursor(InputTable, [Gebied, 'Taw']) as uc:
        for row in uc:
            ##            AddMessage("row = %s" %row)
            row[1] = '?'
            for taw, gebied in AfdelingGebied.items():
                ##                AddMessage("taw = %s" %taw)
                ##                AddMessage("gebied = %s" %gebied)
                for g in gebied:
                    ##                    AddMessage("g= %s" %g)
                    if str(g) in str(row[0]):  # aangepast voor getallen
                        ##                        PrintMessage(str(g))
                        row[1] = taw

            uc.updateRow(row)


def BerekenMeasurelengte(InputTable, Beginpositie, Eindpositie, veldnaam):
    from arcpy import AddField_management, CalculateField_management
    PrintMessage("maak veld 'lengte' en bereken")
    AddField_management(InputTable, veldnaam, "DOUBLE", "#", "#", 9)  # maak veld 'lengte' aan
    expression = 'abs(!%s! - !%s!)' % (Eindpositie, Beginpositie)
    Message = "expression : %s" % expression;
    PrintMessage(Message)
    CalculateField_management(InputTable, veldnaam, expression, "PYTHON_9.3", "#")


def BerekenPercentageMlengte(InputTable, LengteVeld):
    import arcpy
    # bereken totale lengte
    count = arcpy.GetCount_management(InputTable)
    PrintMessage("aantal records: " + str(count))
    TotaleLengte = 0
    SearchField = []
    SearchField.append(LengteVeld)
    print(SearchField)
    for row in arcpy.da.SearchCursor(InputTable, SearchField):
        if row[0] != None:
            TotaleLengte += row[0]
    Message = ("totale lengte: %s m") % str(TotaleLengte)
    PrintMessage(Message)
    # percentages berekenen
    arcpy.AddField_management(InputTable, "PercentageMlengte", "Double")
    expression = "!%s! / %s * 100" % (LengteVeld, TotaleLengte)
    arcpy.CalculateField_management(InputTable, "PercentageMlengte", expression, "PYTHON_9.3")


def BerekenPercentageMlengtePerGroep2(InputTable, LengteVeld, ListGroepveld):
    # overbodig ??????????????
    import arcpy
    Message = (InputTable, LengteVeld, ListGroepveld)
    PrintMessage(Message)
    # bereken totale lengte
    count = arcpy.GetCount_management(InputTable)
    PrintMessage("aantal records: " + str(count))
    Values = unique_values(InputTable, Groepveld)
    ##    PrintMessage(Values)

    TotaleLengte = {}
    for Value in Values:
        TotaleLengte[Value] = 0

    SearchFields = []
    for Veld in ListGroepveld:
        SearchFields.append(Veld)
    SearchFields.append(LengteVeld)
    ##    print (SearchFields)
    for row in arcpy.da.SearchCursor(InputTable, SearchFields):
        if row[0] != None:
            Groep = row[0]
            TotaleLengte[Groep] += row[1]

    arcpy.AddField_management(InputTable, "PercentageMlengte", "Double")
    SearchFields.append("PercentageMlengte")
    with arcpy.da.UpdateCursor(InputTable, SearchFields) as uc:
        for row in uc:
            if row[0] != None:
                row[2] = row[1] / TotaleLengte[row[0]] * 100
                uc.updateRow(row)


def BerekenPercentageMlengtePerGroep(InputTable, LengteVeld, ListGroepveld):
    import arcpy
    ##    PrintMessage("InputTable = %s, LengteVeld = %s, ListGroepveld = %s" % (InputTable, LengteVeld, ListGroepveld) )
    # bereken totale lengte
    count = arcpy.GetCount_management(InputTable)
    PrintMessage("aantal records: %s" % str(count))
    # maak lijst van unieke waarden voor een veld of combinatie van velden
    Values = UniqueValuesMultiField(InputTable, ListGroepveld)
    ##    PrintMessage ("unieke waarden zijn : %s" % Values)
    # bereken totale lengte voor  elke unieke waarde of combinatie van unieke waarden
    TotaleLengte = {}
    for Value in Values:
        TotaleLengte[Value] = 0
    SearchFields = [LengteVeld]
    for Veld in ListGroepveld:
        SearchFields.append(Veld)
    ##        PrintMessage("SearchFields = %s" % SearchFields)
    with arcpy.da.SearchCursor(InputTable, SearchFields) as sc:
        for row in sc:
            ##            PrintMessage("-------")
            ##            PrintMessage(row)
            ##            PrintMessage("-------")
            if row[0] != None:
                Groep = (row[1:])
                ##                PrintMessage ("Groep = %s" %Groep)
                ##                PrintMessage ("TotaleLengte = %s" %TotaleLengte)

                TotaleLengte[Groep] += row[0]
    ##    PrintMessage("Totale lengte = %s" % TotaleLengte)

    arcpy.AddField_management(InputTable, "PercentageMlengte", "Double")  # voeg nieuw percentageveld toe
    SearchFields.insert(0, "PercentageMlengte")  # nieuw veld vooraan in lijst plaatsen
    print([f.name for f in arcpy.ListFields(InputTable)])
    ##    PrintMessage("Searchfield = %s" % SearchFields)
    with arcpy.da.UpdateCursor(InputTable, SearchFields) as uc:
        for row in uc:
            if row[1] != None:
                Groep = tuple(row[2:])
                ##                PrintMessage("PercentageMlengte = %s, Mlengte = %s, TotaleLengte[Groep] = %s , Groep = %s" %(row[0], row[1] , TotaleLengte[Groep], Groep) )
                ##                print 'info',row[0] , row[1] , TotaleLengte[Groep]
                ##                print 'TotaleLengte[Groep]:' ,Groep, TotaleLengte[Groep]
                try:
                    row[0] = row[1] / TotaleLengte[Groep] * 100
                except:
                    row[0] = -999

                uc.updateRow(row)


def UniqueValues(table, field):
    # geeft een lijst van unieke waarden voor een attribuut
    import arcpy
    uniqueValues = set([row[0] for row in arcpy.da.SearchCursor(table, [field])])
    return uniqueValues


##    with arcpy.da.SearchCursor(table, [field]) as cursor:
##        return sorted({str(row[0]) for row in cursor})


def UniqueValuesMultiField(table, listFields):
    # geeft een lijst van unieke combinaties van waarden voor meerdere attributen
    import arcpy
    arcpy.AddMessage('listFields: %s' % listFields)

    with arcpy.da.SearchCursor(table, listFields) as cursor:
        return sorted({(row) for row in cursor})


def ZoekDubbeleWaarden(inputTable, listFields):
    # geeft een lijst van combinaties van waarden voor meerdere attributen die meerdere malen voor komen
    import arcpy
    DuplicateValues = []
    with arcpy.da.SearchCursor(inputTable, listFields) as Sc:
        Rows = [Row for Row in Sc]
    RowsCount = {x: Rows.count(x) for x in Rows}

    return RowsCount


def GebiedPuntEvent(PointFeaureClass, Gebied):  # WERKT NIET
    import arcpy
    arcpy.OverlayRouteEvents_lr(PointFeaureClass, in_event_properties, Gebied, in_event_properties, "UNION", out_event_properties)


def LsControleerBestaanIdent8(opener, ident8):
    # controleert of een ident8 bestaat in locatieservices
    import urllib, json
    teller = 0
    status = 'start'
    while status == 'start' and teller < 10:
        try:
            if teller > 0:
                Message = 'poging %s' % teller
                PrintMessage(Message)
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
        except:
            teller += 1
    if status == 'start':
        return 'error onbekend'


def LsLijstBestaandeWegnummers(opener, omgeving="productie"):
    # controleert of een ident8 bestaat in locatieservices
    import urllib, json, arcpy
    arcpy.AddMessage("maak een lijst van wegnummers voorkomend in locatieservices op %s" % omgeving)
    teller = 0
    status = 'start'
    url = "https://services.apps.mow.vlaanderen.be/locatieservices/cert/rest/locatie/weg"
    if omgeving == "dev":
        arcpy.AddWarning("LsLijstBestaandeWegnummers op dev")
        url = "https://services.apps-dev.mow.vlaanderen.be/locatieservices/cert/rest/locatie/weg"

    while status == 'start' and teller < 10:
        try:
            if teller > 0:
                Message = 'poging %s' % teller
                PrintMessage(Message)
            Leesfunctie = opener.open(url)
            status = str(Leesfunctie.getcode())
            if status == '200':
                status = 'ok'
                lijstIdent8 = json.loads(Leesfunctie.read())  # OK
                return lijstIdent8

            elif status == '404':
                return 'status 404'
        except:
            teller += 1
    if status == 'start':
        return 'error onbekend'

    return lijstIDent8


def LsGetPositieFromOpschriftAfstand(Locaties, legacy, benader, opener):
    ##    PrintMessage("test")
    ##    PrintMessage(Locaties)
    # vraag positie, paal en afstand op, op basis van ident8 en coordinaten
    # legacy true = maak gebruik van relatieve hmlocaties indien er geen palen zijn
    # benader true =  snap naar eindpunten indien de locatie niet loodrecht geprojecteerd kan worden op de route

    import json, urllib2
    # vraag locatie op
    teller = 0  # teller telt aantal pogingen tot opvragen van de positie
    status = -1  # default waarde
    Url = "https://services.apps.mow.vlaanderen.be/locatieservices/cert/rest/locatie/weglocatie?"
    Url = "https://services.apps.mow.vlaanderen.be/locatieservices/cert/rest/locatie/weglocatie?legacy=%s&benader=%s" % (
    legacy, benader)
    PrintMessage(Url)
    # vb    Locaties = [{ "ident8": "N2820001", "opschrift": 100, 'afstand':50 ,"bron": "relatief"},{ "ident8": "N2820001", "opschrift": 10, 'afstand':0, "bron": "relatief"},]

    # vraag locaties op met een maximaal aantal locaties per keer
    start = 0
    aantal = 1000
    stop = aantal
    totaal = len(Locaties)
    ##    PrintMessage("Locaties = %s" %str(Locaties))
    PrintMessage(('totaal aantal opgevraagde', str(totaal)))

    while start < totaal:
        status = -1  # default waarde
        jsonArgs = json.dumps(Locaties[start:stop])
        ##        PrintMessage(jsonArgs)
        PrintMessage(('\nstart', str(start), 'stop', str(stop)))
        ##        PrintMessage(('jsonArgs:',jsonArgs))
        ##        PrintMessage(('Locaties:',str(Locaties)))

        while status not in (200, 404) and teller < 10:  # probeer meerdere malen indien  ls niet reageerd
            ##                PrintMessage('voer request uit')
            ##            try:
            if teller > 0:
                Message = 'poging %s' % teller
                PrintMessage(Message)

            # voer request uit
            PrintMessage('voer request uit')
            req = urllib2.Request(Url, data=jsonArgs, headers={"Content-Type": "application/vnd.awv.wdb-v3.0+json"})

            Message = 'Url = %s' % Url;
            PrintMessage(Message)
            Leesfunctie = opener.open(req)
            status = (Leesfunctie.getcode())
            PrintMessage(('status:', str(status)))
            if status == 200:
                ##                    PrintMessage("status ok")
                OpgevraagdeLocaties = json.loads(Leesfunctie.read())  # OK
                ##                    PrintMessage(('opgevraagde locaties',str(OpgevraagdeLocaties)))

                # als status goed is, lees dan positie uit de json
                for OpgevraagdeLocatie, arg in zip(OpgevraagdeLocaties, Locaties[start:stop]):
                    PrintMessage("opgevraagde locatie : %s" % OpgevraagdeLocatie)
                    try:
                        coordinates = json.dumps(OpgevraagdeLocatie['success']['geometry']['coordinates'])
                        positie = json.dumps(OpgevraagdeLocatie['success']['positie'], indent=4, sort_keys=True).replace(".", ",")
                        ##                            PrintMessage("coordinates:%s"%coordinates)
                        arg['coordinates'] = coordinates
                        arg['positie'] = positie
                    ##                            PrintMessage("opgevraagde locatie 2: %s" %OpgevraagdeLocatie)
                    except:
                        print(OpgevraagdeLocatie)
                        if 'is geen bestaande weg' in str(OpgevraagdeLocatie):
                            PrintMessage(("de ident8 of het opschrift bestaat niet!!!", str(OpgevraagdeLocatie)))
                            arg['positie'] = -2
                        ##                                arg['afstand'] =-2
                        else:
                            PrintMessage(('Probleem bij het opvragen van de locatie:', str(OpgevraagdeLocatie)))
                            arg['positie'] = -3
        ##                                arg['afstand'] =-3

        ##                    PrintMessage(('Locaties:',str(Locaties)))
        ##            except: #request is niet gelukt
        ##                teller+=1
        start += aantal
        stop += aantal

    OpgevraagdeLocaties = Locaties
    ##    PrintMessage(('opgevraagdelocaties:',str(OpgevraagdeLocaties)))
    Message = "Locaties opgevraagd";
    PrintMessage(Message)
    return OpgevraagdeLocaties


def LsGetOpschriftAfstandWegLocatieFromPositie(Locaties, legacy, benader, opener):
    import arcpy
    ##    PrintMessage("test")
    ##    PrintMessage(Locaties)
    ##    return 0,0
    # vraag positie, paal en afstand op, op basis van ident8 en coordinaten
    # legacy true = maak gebruik van relatieve hmlocaties indien er geen palen zijn
    # benader true =  snap naar eindpunten indien de locatie niet loodrecht geprojecteerd kan worden op de route

    import json, urllib2

    # vraag locatie op
    teller = 0  # teller telt aantal pogingen tot opvragen van de positie
    status = -1  # default waarde
    ##    Url = "https://services.apps.mow.vlaanderen.be/locatieservices/cert/rest/locatie/weglocatie?benader=True" !!! vervangen door onderstaande 201712
    Url = "https://services.apps.mow.vlaanderen.be/locatieservices/cert/rest/locatie/weglocatie?legacy=%s&benader=%s" % (
    legacy, benader)
    Message = "Url = %s" % (Url);
    PrintMessage(Message)
    # vb
    ##    Locaties = [{ "ident8": "N2820001", "positie": 10, 'benader' : True ,"bron": "positie"},{ "ident8": "N2820001", "positie": 10, 'benader' : True ,"bron": "positie"},]

    start = 0
    aantal = 2000
    stop = aantal
    totaal = len(Locaties)
    PrintMessage(('totaal opgevraagde locaties', str(totaal)))

    while start < totaal:
        status = -1  # default waarde
        jsonArgs = json.dumps(Locaties[start:stop])
        PrintMessage(('\nstart', str(start), 'stop', str(stop)))
        ##        PrintMessage(('jsonArgs:',jsonArgs))
        ##        PrintMessage(('Locaties:',str(Locaties)))

        while status not in (200, 404) and teller < 10:  # probeer meerdere malen indien  ls niet reageerd
            ##            try:
            if teller > 0:
                Message = 'poging %s' % teller
                PrintMessage(Message)

            # voer request uit
            PrintMessage('voer request uit')
            ##                opener.addheaders = [("Accept" , "application/vnd.geolatte-featureserver+csv")]
            req = urllib2.Request(Url, data=jsonArgs, headers={"Content-Type": "application/vnd.awv.wdb-v3.0+json"})
            try:
                Leesfunctie = opener.open(req)
            except Exception as e:
                arcpy.AddError("heeft elk record een ident8 en posities?")
                arcpy.AddError(e)

            status = (Leesfunctie.getcode())
            if status == 200:
                ##                    PrintMessage("status ok")
                OpgevraagdeLocaties = json.loads(Leesfunctie.read())  # OK
                ##                PrintMessage(('opgevraagde locaties',str(OpgevraagdeLocaties)))
                # als status goed is, lees dan positie uit de json
                for OpgevraagdeLocatie, arg in zip(OpgevraagdeLocaties, Locaties[start:stop]):
                    try:
                        opschrift = json.dumps(OpgevraagdeLocatie['success']['opschrift'], indent=4, sort_keys=True).replace(".",
                                                                                                                             ",")
                        afstand = json.dumps(OpgevraagdeLocatie['success']['afstand'], indent=4, sort_keys=True).replace(".", ",")
                        arg['opschrift'] = opschrift
                        arg['afstand'] = afstand
                    ##                            print 'opschrift:',opschrift,'afstand',afstand,arg
                    except:
                        ##                            print OpgevraagdeLocatie
                        if 'is geen bestaande weg' in str(OpgevraagdeLocatie):
                            PrintMessage(("de ident8 of het opschrift bestaat niet!!!", str(OpgevraagdeLocatie)))
                            arg['opschrift'] = -2
                            arg['afstand'] = -2
                        else:
                            PrintMessage(('Probleem bij het opvragen van de locatie:', str(OpgevraagdeLocatie)))
                            arg['opschrift'] = -3
                            arg['afstand'] = -3
        ##                    PrintMessage(('Locaties:',str(Locaties)))
        ##            except: #request is niet gelukt
        ##                teller+=1
        start += aantal
        stop += aantal

    OpgevraagdeLocaties = Locaties
    ##    PrintMessage(('opgevraagdelocaties:',str(OpgevraagdeLocaties)))
    return OpgevraagdeLocaties


def LsGetRelatieveWegLocatieFromXY(Locaties, opener):
    ##    Message = 'Locaties:%s' %Locaties;PrintMessage(Message)
    # vraag positie, paal en afstand op, op basis van ident8 en coordinaten
    # legacy true = maak gebruik van relatieve hmlocaties indien er geen palen zijn
    # benader true =  snap naar eindpunten indien de locatie niet loodrecht geprojecteerd kan worden op de route

    import json, urllib2
    OntvangenLocaties = []
    # vraag locatie op
    teller = 0  # teller telt aantal pogingen tot opvragen van de positie
    status = -1  # default waarde
    ##    Url = "https://services.apps.mow.vlaanderen.be/locatieservices/cert/rest/locatie/weglocatie?benader=True"
    # https://apps.mow.vlaanderen.be/locatieservices/rest/locatie/weglocatie/relatief/via/xy?y=166734.290&x=137608.885&bronCrs=31370&doelCrs=31370
    Url = "https://services.apps.mow.vlaanderen.be/locatieservices/cert/rest/locatie/weglocatie/?benader=true"
    # vb    locaties = [ { "ident8": "N0100001", "bron": "gps", "geometry": {"crs": {"type": "name","properties": {"name": "EPSG:31370"}},"type": "Point", "coordinates": [ 183434, 185706  ] } },{ "ident8": "N0100002", "bron": "gps", "geometry": {"crs": {"type": "name","properties": {"name": "EPSG:31370"}},"type": "Point", "coordinates": [ 183434.5, 185706.5] } }]

    # vraag locaties op met een maximaal aantal locaties per keer
    start = 0
    aantal = 1000
    stop = aantal
    totaal = len(Locaties)
    PrintMessage(('totaal opgevraagde locaties', str(totaal)))

    while start < totaal:
        status = -1  # default waarde
        jsonArgs = json.dumps(Locaties[start:stop])
        PrintMessage(('\nstart', str(start), 'stop', str(stop)))
        ##        PrintMessage(('jsonArgs:',jsonArgs))

        while status not in (200, 404) and teller < 10:  # probeer meerdere malen indien  ls niet reageerd
            ##                PrintMessage('voer request uit')
            ##            try:
            if teller > 0:
                Message = 'poging %s' % teller
                PrintMessage(Message)

            # voer request uit
            PrintMessage('voer request uit')
            ##                Message = 'URL: %s, data=jsonArgs;%s' %(Url,jsonArgs); PrintMessage(Message)
            req = urllib2.Request(Url, data=jsonArgs, headers={"Content-Type": "application/vnd.awv.wdb-v3.0+json"})
            print(str(req))
            ##                req = urllib2.Request("https://services.apps.mow.vlaanderen.be/locatieservices/cert/rest/weglocatie/")

            Leesfunctie = opener.open(req)
            status = (Leesfunctie.getcode())
            ##                PrintMessage(('status:',str(status)))
            if status == 200:
                PrintMessage("status ok")
                OpgevraagdeLocaties = json.loads(Leesfunctie.read())  # OK

                for Locatie in OpgevraagdeLocaties:
                    OntvangenLocaties.append(Locatie)
                ##                    PrintMessage(('opgevraagde locaties',str(OpgevraagdeLocaties)))

                # als status goed is, lees dan positie uit de json
                for OpgevraagdeLocatie, arg in zip(OpgevraagdeLocaties, Locaties[start:stop]):
                    try:
                        positie = json.dumps(OpgevraagdeLocatie['success']['positie'], indent=4, sort_keys=True).replace(".", ",")
                        ##                            afstand =  json.dumps(OpgevraagdeLocatie['success']['afstand'], indent=4, sort_keys=True).replace(".",",")
                        arg['positie'] = positie
                        ##                            arg['afstand'] = afstand
                        print('positie: %s' % positie)
                    ##                            print 'afstand:',afstand
                    except:
                        print(OpgevraagdeLocatie)
                        if 'is geen bestaande weg' in str(OpgevraagdeLocatie):
                            PrintMessage(("de ident8 of het opschrift bestaat niet!!!", str(OpgevraagdeLocatie)))
                            arg['positie'] = -2
                        ##                                arg['afstand'] =-2
                        else:
                            PrintMessage(('Ongekend probleem:', str(OpgevraagdeLocatie)))
                            arg['positie'] = -3
        ##                                arg['afstand'] =-3

        ##                    PrintMessage(('Locaties:',str(Locaties)))
        ##            except: #request is niet gelukt
        ##                teller+=1
        start += aantal
        stop += aantal

    ##    OpgevraagdeLocaties = Locaties
    ##    PrintMessage(('OntvangenLocaties:',str(OntvangenLocaties)))
    return OntvangenLocaties


def LsGetRelatieveWegLocatieFromXYSingle(x, y, opener):
    ##    Message = 'Locaties:%s' %Locaties;PrintMessage(Message)
    # vraag positie, paal en afstand op, op basis van coordinaten
    # legacy true = maak gebruik van relatieve hmlocaties indien er geen palen zijn
    # benader true =  snap naar eindpunten indien de locatie niet loodrecht geprojecteerd kan worden op de route

    import json, urllib2
    # vraag locatie op
    teller = 0  # teller telt aantal pogingen tot opvragen van de positie
    status = -1  # default waarde
    # https://apps.mow.vlaanderen.be/locatieservices/rest/locatie/weglocatie/relatief/via/xy?y=166734.290&x=137608.885&bronCrs=31370&doelCrs=31370

    Url = "https://services.apps.mow.vlaanderen.be/locatieservices/cert/rest/locatie/weglocatie/via/xy?x=%s&y=%s&bronCrs=31370&doelCrs=31370" % (
    x, y)
    print(Url)

    status = -1  # default waarde

    while status not in (200, 404) and teller < 10:  # probeer meerdere malen indien  ls niet reageerd
        ##                PrintMessage('voer request uit')

        if teller > 0:
            Message = 'poging %s' % teller
        ##            PrintMessage(Message)

        # voer request uit
        ##        PrintMessage('voer request uit')
        req = urllib2.Request(Url, headers={"Content-Type": "application/vnd.awv.wdb-v3.0+json"})
        print(str(req))
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


def LsGetCoordinatesFromIdent8OpschirftAfstandSingle(Ident8, Opschrift, Afstand, opener):
    ##    Message = 'Locaties:%s' %Locaties;PrintMessage(Message)
    # vraag positie, paal en afstand op, op basis van coordinaten
    # legacy true = maak gebruik van relatieve hmlocaties indien er geen palen zijn
    # benader true =  snap naar eindpunten indien de locatie niet loodrecht geprojecteerd kan worden op de route

    import json, urllib2
    # vraag locatie op
    teller = 0  # teller telt aantal pogingen tot opvragen van de positie
    status = -1  # default waarde
    # https://apps.mow.vlaanderen.be/locatieservices/rest/locatie/weglocatie/relatief/via/xy?y=166734.290&x=137608.885&bronCrs=31370&doelCrs=31370

    Url = "https://services.apps.mow.vlaanderen.be/locatieservices/cert/rest/locatie/weglocatie?ident8=%s&opschrift=%s&afstand=%s&bronCrs=31370&doelCrs=31370" % (
    Ident8, Opschrift, Afstand)
    print(Url)

    status = -1  # default waarde

    while status not in (200, 404) and teller < 10:  # probeer meerdere malen indien  ls niet reageerd
        if teller > 0:
            Message = 'poging %s' % teller  ##;PrintMessage(Message)

        # voer request uit
        ##        PrintMessage('voer request uit')
        req = urllib2.Request(Url, headers={"Content-Type": "application/vnd.awv.wdb-v3.0+json"})
        ##        print str(req)

        Leesfunctie = opener.open(req)
        status = (Leesfunctie.getcode())  ##;PrintMessage(('status:',str(status)))

        if status == 200:
            ##            PrintMessage("status ok")
            OpgevraagdeLocaties = json.loads(Leesfunctie.read())  # OK
            ##            PrintMessage(OpgevraagdeLocaties)
            OpgevraagdeLocatie = OpgevraagdeLocaties["geometry"]["coordinates"]

    return OpgevraagdeLocatie


def MaakCoordinatenVeldVanOpschriftAfstand(InputTable, Ident8, BeginOpschrift, BeginAfstand, EindOpschrift, EindAfstand, legacy,
                                           benader, beginX, beginY, eindX, eindY):
    # maak positievelden aan op basis van ident8 en xy-locatie
    from arcpy import AddMessage, ListFields
    import json

    legacy, benader = legacy.lower(), benader.lower()
    if legacy not in ('true', 'false') or benader not in ('true', 'false'):
        PrintMessage('invoer legacy/benader moet de waarde true of false hebben, huidige waarde = %s,%s' % (legacy, benader))
        AddMessage("huidige waarde = %s, %s" % (legacy, benader))
    opener = Certificaat("productie")
    from arcpy import AddField_management
    from arcpy.da import UpdateCursor, SearchCursor

    # eventtype bepalen
    if EindAfstand == '':
        EventType = 'PointEvent'
        RelPosities = [[beginX, beginY]]
        AbsPosities = (BeginOpschrift, BeginAfstand)
    else:
        EventType = 'LineEvent'
        RelPosities = [[beginX, beginY], [eindX, eindY]]
        AbsPosities = (BeginOpschrift, BeginAfstand, EindOpschrift, EindAfstand)
    ##    PrintMessage(AbsPosities)

    # wijzig veldnamen indien de inputfc een shapefile is
    if InputTable.split('.')[-1] in ('shp', 'dfb'):
        ##        RelPosities = [RelPositie[:10] for RelPositie in RelPosities]
        AbsPosities = [AbsPositie[:10] for AbsPositie in AbsPosities]

    for RelPositie in RelPosities:
        PrintMessage("Relpositie = %s, Relposities = %s" % (RelPositie, RelPosities))
        PrintMessage('start berekening %s' % RelPositie)

        # inputvelden afhankelijk maken van positie beginpositie of eindpositie
        if RelPositie == [[beginX, beginY], [eindX, eindY]]:
            Opschrift = AbsPosities[2]
            Afstand = AbsPosities[3]
        else:
            Opschrift = AbsPosities[0]
            Afstand = AbsPosities[1]

        # maak velden aan
        for field in (RelPositie):
            PrintMessage('maak veld %s aan' % field)
            if field not in [f.name for f in ListFields(InputTable)]:
                AddField_management(InputTable, field, 'DOUBLE')

        # ga door de data, lees de posities en bereken de posities voor de gevraagde velden
        Locaties = []
        with SearchCursor(InputTable, [Ident8, Opschrift, Afstand]) as sc:
            PrintMessage("%s, %s, %s" % (Ident8, Opschrift, Afstand))
            for row in sc:
                ##                PrintMessage(row)
                Locatie = {'bron': 'relatief', 'ident8': row[0], 'opschrift': float(row[1]), 'afstand': float(row[2])}
                Locaties.append(Locatie)
        ##        PrintMessage(('locaties',str(Locaties)))
        OpgevraagdeLocaties = LsGetPositieFromOpschriftAfstand(Locaties, legacy, benader, opener)
        ##        PrintMessage(str(OpgevraagdeLocaties))
        PrintMessage('Aantal ontvangen locaties: %s' % len(OpgevraagdeLocaties))

        # schrijf de locaties weg
        with UpdateCursor(InputTable, [Ident8, RelPositie[0], RelPositie[1], Opschrift, Afstand]) as uc:
            Message = "Schrijf locaties weg";
            PrintMessage(Message)
            teller = 0
            for row in uc:
                teller += 1
                if teller / 1000.0 == teller / 1000:
                    Message = "%s locaties weggeschreven" % teller;
                    PrintMessage(Message)
                    Message = "%s elementen in OpgevraagdeLocaies" % len(OpgevraagdeLocaties);
                    PrintMessage(Message)
                ##                PrintMessage(('row in uc:',str(row)))
                ##                PrintMessage(('Opgevraagde Locatie:',str(OpgevraagdeLocaties)))
                # zoek naar de juiste link tussen row en jsonobject
                OpgevraagdeLocatie = (OpgevraagdeLocatie for OpgevraagdeLocatie in OpgevraagdeLocaties if
                                      OpgevraagdeLocatie["ident8"] == row[0] and float(OpgevraagdeLocatie["opschrift"]) == row[
                                          3] and float(OpgevraagdeLocatie["afstand"]) == row[4]).next()
                ##                PrintMessage("OpgevraagdeLocaties [0] : %s" %OpgevraagdeLocaties[0])
                ##                PrintMessage("OpgevraagdeLocatie : %s" %OpgevraagdeLocatie)
                coordinates = json.loads(OpgevraagdeLocatie['coordinates'])
                row[1] = coordinates[0]
                row[2] = coordinates[1]
                ##                del OpgevraagdeLocaties[OpgevraagdeLocaties.index(OpgevraagdeLocatie)]
                ##                PrintMessage(('row:',str(row)))
                uc.updateRow(row)

        Message = "Locaties wegeschreven naar tabel";
        PrintMessage(Message)


def MaakPositieVeldVanOpschriftAfstand(InputTable, Ident8, BeginOpschrift, BeginAfstand, EindOpschrift, EindAfstand, legacy,
                                       benader, OutputBeginPositie, OutputEindPositie):
    # maak positievelden aan op basis van ident8 en xy-locatie
    from arcpy import AddMessage
    if legacy not in ('true', 'false') or benader not in ('true', 'false'):
        PrintMessage('invoer legacy/benader moet de waarde true of false hebben')
        AddMessage("huidige waarde = %s, %s" % (legacy, benader))
    opener = Certificaat("productie")
    from arcpy import AddField_management
    from arcpy.da import UpdateCursor, SearchCursor

    # eventtype bepalen
    if EindAfstand == '':
        EventType = 'PointEvent'
        RelPosities = (OutputBeginPositie,)
        AbsPosities = (BeginOpschrift, BeginAfstand)
    else:
        EventType = 'LineEvent'
        RelPosities = (OutputBeginPositie, OutputEindPositie)
        AbsPosities = (BeginOpschrift, BeginAfstand, EindOpschrift, EindAfstand)
    ##    PrintMessage(AbsPosities)

    # wijzig veldnamen indien de inputfc een shapefile is
    if InputTable.split('.')[-1] in ('shp', 'dfb'):
        ##        RelPosities = [RelPositie[:10] for RelPositie in RelPosities]
        AbsPosities = [AbsPositie[:10] for AbsPositie in AbsPosities]

    for RelPositie in RelPosities:
        Message = 'start berekening %s' % RelPositie
        PrintMessage(Message)

        # inputvelden afhankelijk maken van positie beginpositie of eindpositie
        if RelPositie == OutputEindPositie:
            Opschrift = AbsPosities[2]
            Afstand = AbsPosities[3]
        else:
            Opschrift = AbsPosities[0]
            Afstand = AbsPosities[1]

        # maak velden aan
        ##        for field in ( RelPositie):
        field = RelPositie
        Message = 'maak veld %s aan' % field
        PrintMessage(Message)
        AddField_management(InputTable, field, 'DOUBLE')

        # ga door de data, lees de posities en bereken de posities voor de gevraagde velden
        Locaties = []
        with SearchCursor(InputTable, [Ident8, RelPositie, Opschrift, Afstand]) as sc:
            print("%s, %s, %s, %s" % (Ident8, RelPositie, Opschrift, Afstand))
            for row in sc:
                Locatie = {'bron': 'relatief', 'ident8': row[0], 'opschrift': float(row[2]), 'afstand': float(row[3])}
                Locaties.append(Locatie)
        ##        PrintMessage(('locaties',str(Locaties)))
        OpgevraagdeLocaties = LsGetPositieFromOpschriftAfstand(Locaties, legacy, benader, opener)
        ##        PrintMessage(str(OpgevraagdeLocaties))
        Message = 'Aantal ontvangen locaties: %s' % len(OpgevraagdeLocaties);
        PrintMessage(Message)

        # schrijf de locaties weg
        with UpdateCursor(InputTable, [Ident8, RelPositie, Opschrift, Afstand]) as uc:
            Message = "Schrijf locaties weg";
            PrintMessage(Message)
            teller = 0
            for row in uc:
                teller += 1
                if teller / 1000.0 == teller / 1000:
                    Message = "%s locaties weggeschreven" % teller;
                    PrintMessage(Message)
                    Message = "%s elementen in OpgevraagdeLocaies" % len(OpgevraagdeLocaties);
                    PrintMessage(Message)
                ##                PrintMessage(('row in uc:',str(row)))
                ##                PrintMessage(('Opgevraagde Locatie:',str(OpgevraagdeLocaties)))
                # zoek naar de juiste link tussen row en jsonobject
                OpgevraagdeLocatie = (OpgevraagdeLocatie for OpgevraagdeLocatie in OpgevraagdeLocaties if
                                      OpgevraagdeLocatie["ident8"] == row[0] and float(OpgevraagdeLocatie["opschrift"]) == row[
                                          2] and float(OpgevraagdeLocatie["afstand"]) == row[3]).next()
                PrintMessage(OpgevraagdeLocatie)
                row[1] = OpgevraagdeLocatie['positie']
                del OpgevraagdeLocaties[OpgevraagdeLocaties.index(OpgevraagdeLocatie)]
                ##                PrintMessage(('row:',str(row)))
                uc.updateRow(row)

        Message = "Locaties wegeschreven naar tabel";
        PrintMessage(Message)


def MaakPositieVeldenFromXY(InputTable, Ident8, BeginX, BeginY, EindX, EindY, legacy, benader):
    # maak positievelden aan op basis van ident8 en xy-locatie
    if legacy not in ('true', 'false') or benader not in ('true', 'false'):
        PrintMessage('invoer legacy/benader moet de waarde true of false hebben')

    import sys, arcpy
    print(sys.version)
    arcpy.AddMessage("python versie = %s" % sys.version)
    if str(sys.version)[0] == "2":
        opener = Certificaat("productie")
    elif str(sys.version)[0] == "3":
        opener = CertificaatPython3("productie")

    from arcpy import AddField_management
    from arcpy.da import UpdateCursor

    # invoer Shape aanpassen
    if BeginX == 'SHAPE': BeginX += '@'
    if BeginY == 'SHAPE': BeginY += '@'
    if EindX == 'SHAPE': EindX += '@'
    if EindY == 'SHAPE': EindY += '@'

    # eventtype bepalen
    if EindX in ('', '#', None):
        EventType = 'PointEvent'
        RelPosities = ('positie',)
        AbsPosities = ('opschrift', 'afstand')
    else:
        EventType = 'LineEvent'
        RelPosities = ('beginpositie', 'eindpositie')
        AbsPosities = ('beginopschrift', 'beginafstand', 'eindopschrift', 'eindafstand')
    PrintMessage('Eventtype: ' + EventType)

    # wijzig veldnamen indien de inputfc een shapefile is
    if InputTable.split('.')[-1] in ('shp', 'dfb'):
        RelPosities = [RelPositie[:10] for RelPositie in RelPosities]
        AbsPosities = [AbsPositie[:10] for AbsPositie in AbsPosities]

    for RelPositie in RelPosities:
        Message = 'start berekening %s' % RelPositie
        PrintMessage(Message)

        # inputvelden afhankelijk maken van positie beginpositie of eindpositie
        if RelPositie == 'eindpositie':
            CoordinateX = EindX
            CoordinateY = EindY
            Opschrift = AbsPosities[2]
            Afstand = AbsPosities[3]

        else:
            CoordinateX = BeginX
            CoordinateY = BeginY
            Opschrift = AbsPosities[0]
            Afstand = AbsPosities[1]

        # maak velden aan
        for field in (RelPositie, Opschrift, Afstand):
            Message = 'maak veld %s aan' % field
            PrintMessage(Message)
            AddField_management(InputTable, field, 'DOUBLE')

        # ga door de data en bereken de posities voor het gevraagde veld
        Locaties = []
        with UpdateCursor(InputTable, [Ident8, CoordinateX, CoordinateY, RelPositie, Opschrift, Afstand]) as uc:
            print("%s,%s,%s,%s,%s,%s" % (Ident8, CoordinateX, CoordinateY, RelPositie, Opschrift, Afstand))
            teller = 0
            for row in uc:
                ##                PrintMessage(CoordinateX)
                if CoordinateX != 'SHAPE@' and CoordinateY != 'SHAPE@':
                    X = row[1]; Y = row[2]
                elif CoordinateX != CoordinateY:
                    PrintMessage('niet gelijke geometryvelden')
                elif RelPositie != 'eindpositie':
                    X = row[1].firstPoint.X; Y = row[1].firstPoint.Y  # veld is SHAPE
                elif RelPositie == 'eindpositie':
                    X = row[2].lastPoint.X; Y = row[2].lastPoint.Y  # veld is SHAPE

                ##                Message='X: %s' % str(X); PrintMessage(Message)

                geometry = {"crs": {"type": "name", "properties": {"name": "EPSG:31370"}}, "type": "Point", "coordinates": [X, Y]}
                ##                Message='coordinates: %s' % str([ X, Y]); PrintMessage(Message)
                ##                Message='geometry: %s' %geometry; PrintMessage(Message)
                Locatie = {'bron': 'gps', 'ident8': row[0], 'geometry': geometry}
                Locaties.append(Locatie)

        ##        PrintMessage(('locaties',str(Locaties)))
        OpgevraagdeLocaties = LsGetRelatieveWegLocatieFromXY(Locaties, opener)
        ##        PrintMessage(str(OpgevraagdeLocaties))
        Message = 'Aantal ontvangen locaties: %s' % len(OpgevraagdeLocaties);
        PrintMessage(Message)

        ##        PrintMessage('OpgevraagdeLocaties: ' +str(OpgevraagdeLocaties))

        # schrijf de locaties weg
        with UpdateCursor(InputTable, [Ident8, CoordinateX, CoordinateY, RelPositie, Opschrift, Afstand]) as uc:
            for row in uc:
                if CoordinateX != 'SHAPE@' and CoordinateY != 'SHAPE@':
                    X = row[1]; Y = row[2]
                elif CoordinateX != CoordinateY:
                    PrintMessage('niet gelijke geometryvelden')
                elif RelPositie != 'eindpositie':
                    X = row[1].firstPoint.X; Y = row[1].firstPoint.Y;  # veld is SHAPE
                elif RelPositie == 'eindpositie':
                    X = row[2].lastPoint.X; Y = row[2].lastPoint.Y  # veld is SHAPE
                ##
                ##                PrintMessage(('Opgevraagde Locatie:',str(OpgevraagdeLocaties)))
                # zoek naar de juiste link tussen row en jsonobject
                OpgevraagdeLocatie = (OpgevraagdeLocatie for OpgevraagdeLocatie in OpgevraagdeLocaties if
                                      OpgevraagdeLocatie['success']["ident8"] == row[0] and \
                                      float(OpgevraagdeLocatie['success']['geometry']['coordinates'][0]) == X and \
                                      float(OpgevraagdeLocatie['success']['geometry']['coordinates'][1]) == Y).next()
                ##                PrintMessage(OpgevraagdeLocatie)
                row[3] = OpgevraagdeLocatie['success']['positie']
                row[4] = OpgevraagdeLocatie['success']['opschrift']
                row[5] = OpgevraagdeLocatie['success']['afstand']
                ##                PrintMessage(('row:',str(row)))
                uc.updateRow(row)


def MaakOpschriftAfstandFromPositie(InputTable, Ident8, Beginpositie, Eindpositie, legacy, benader, OutputBeginOpschrift,
                                    OutputBeginAfstand, OutputEindOpschrift, OutputEindAfstand):
    # maak positievelden aan op basis van ident8 en xy-locatie
    if legacy not in ('true', 'false') or benader not in ('true', 'false'):
        PrintMessage('invoer legacy/benader moet de waarde true of false hebben')
    opener = Certificaat("productie")
    import arcpy
    ##    arcpy.AddMessage('TEST'+Eindpositie)
    # eventtype bepalen
    if Eindpositie == '#' or Eindpositie == '':
        EventType = 'PointEvent'
        RelPosities = (Beginpositie,)
        AbsPosities = (OutputBeginOpschrift, OutputBeginAfstand)
    else:
        EventType = 'LineEvent'
        RelPosities = (Beginpositie, Eindpositie)
        AbsPosities = (OutputBeginOpschrift, OutputBeginAfstand, OutputEindOpschrift, OutputEindAfstand)
    ##    arcpy.AddMessage('TEST'+EventType)
    ##    PrintMessage('TEST'+str(RelPosities))

    # wijzig veldnamen indien de inputfc een shapefile is
    if InputTable.split('.')[-1] in ('shp', 'dfb'):
        ##        RelPosities = [RelPositie[:10] for RelPositie in RelPosities]
        AbsPosities = [AbsPositie[:10] for AbsPositie in AbsPosities]

    for RelPositie in RelPosities:
        Message = 'start berekening %s' % RelPositie
        PrintMessage(Message)

        # inputvelden afhankelijk maken van positie beginpositie of eindpositie
        if RelPositie == Eindpositie:
            Opschrift = AbsPosities[2]
            Afstand = AbsPosities[3]
        else:
            Opschrift = AbsPosities[0]
            Afstand = AbsPosities[1]

        # maak velden aan
        for newField in (Opschrift, Afstand):
            if newField not in [bestaandveld.name for bestaandveld in arcpy.ListFields(InputTable)]:
                PrintMessage("maak veld %s aan" % newField)
                arcpy.AddField_management(InputTable, newField, 'DOUBLE')
            else:
                PrintMessage("veld %s bestaat reeds" % newField)

        # ga door de data, lees de posities en bereken de posities voor de gevraagde velden
        Locaties = []
        with arcpy.da.UpdateCursor(InputTable, [Ident8, RelPositie, Opschrift, Afstand]) as sc:
            ##            print Ident8,RelPositie,Opschrift,Afstand
            for row in sc:
                ##                Locatie = {'benader': True, 'bron': 'positie', 'ident8': row[0],'positie': row[1]}
                ##                Locatie = {'benader': benader, 'legacy' : legacy, 'bron': 'positie', 'ident8': row[0],'positie': row[1]}!!!!!!!!!!!!gewijzigd door onderstaande
                Locatie = {'bron': 'positie', 'ident8': row[0], 'positie': row[1]}
                Locaties.append(Locatie)
        ##        PrintMessage(('locaties',str(Locaties)))
        OpgevraagdeLocaties = LsGetOpschriftAfstandWegLocatieFromPositie(Locaties, legacy, benader, opener)
        ##        PrintMessage(str(OpgevraagdeLocaties))
        Message = 'Aantal ontvangen locaties: %s' % len(OpgevraagdeLocaties);
        PrintMessage(Message)

        # schrijf de locaties weg
        OpgevraagdeLocatiesDict = {}
        for OpgevraagdeLocatie in OpgevraagdeLocaties:
            key = (OpgevraagdeLocatie["ident8"], OpgevraagdeLocatie["positie"])
            value = (OpgevraagdeLocatie['opschrift'], OpgevraagdeLocatie['afstand'])
            OpgevraagdeLocatiesDict[key] = value
        PrintMessage('schrijf de locaties weg')
        countOpgevraagdeLocaties = len(OpgevraagdeLocaties)
        del OpgevraagdeLocatie, OpgevraagdeLocaties

        with arcpy.da.UpdateCursor(InputTable, [Ident8, RelPositie, Opschrift, Afstand]) as uc:
            teller = 0
            for row in uc:
                teller += 1
                ##                arcpy.AddMessage(str(OpgevraagdeLocaties))
                ##                OpgevraagdeLocatie = (OpgevraagdeLocatie for OpgevraagdeLocatie in OpgevraagdeLocaties if OpgevraagdeLocatie["ident8"] == row[0] and OpgevraagdeLocatie["positie"] == row[1]).next()
                ##                arcpy.AddMessage(OpgevraagdeLocatiesDict)
                ##                arcpy.AddMessage("-------1")
                ##                arcpy.AddMessage((row[0] , row[1]))
                ##                arcpy.AddMessage("-------2")
                OpgevraagdeLocatie = OpgevraagdeLocatiesDict[(row[0], row[1])]
                ##                arcpy.AddMessage(OpgevraagdeLocatie)
                if teller / 1000.0 == teller / 1000:
                    PrintMessage("Aantal weggeschreven locaties = %s/%s" % (teller, countOpgevraagdeLocaties))
                ##                row[2] = OpgevraagdeLocatie['opschrift']
                ##                row[3] = OpgevraagdeLocatie['afstand']
                row[2] = OpgevraagdeLocatie[0]
                row[3] = OpgevraagdeLocatie[1]
                ##                PrintMessage(('row:',str(row)))
                uc.updateRow(row)


def OverlayRouteEvents_zijde(in_table, in_event_ident8, in_event_beginpositie, in_event_eindpositie, in_event_zijde, in_event,
                             overlay_table, overlay_event_ident8, overlay_event_beginpositie, overlay_event_eindpositie,
                             overlay_event_zijde, overlay_type, out_table, out_event_ident8, out_event_beginpositie,
                             out_event_eindpositie, out_event_zijde):
    # werkt zoals tool overlay events (en maakt hier ook gebruik van) maar kan rekening houden met een tweede routeidentifyveld zoals zijde van de rijbaan
    arcpy.CopyRows_management(in_table, 'in_memory/intable')
    arcpy.CopyRows_management(overlay_table, 'in_memory/overlaytable')

    # maak nieuwe routeidentifier op basis van ident8 en zijde
    for table in ('in_memory/intable', 'in_memory/overlaytable'):
        arcpy.AddField_management(table, 'id8zijde', 'TEXT')

        if in_event_zijde == '#':
            in_table = MaakRowsPerZijde(table)
            in_event_zijde = 'zijderijbaan'
        if overlay_event_zijde == '#':
            overlay_table = MaakRowsPerZijde(table)
            overlay_event_zijde = 'zijderijbaan'
        if table == 'in_memory/intable' and in_event_zijde != '#':
            event_zijde = in_event_zijde
        elif table == 'in_memory/overlaytable' and overlay_event_zijde != '#':
            event_zijde = overlay_event_zijde

        expression = '!%s! + !%s!' % (overlay_event_ident8, event_zijde)
        print(expression)
        arcpy.CalculateField_management(table, 'id8zijde', expression, 'PYTHON_9.3')

    in_event_properties = 'id8zijde LINE %s %s' % (in_event_beginpositie, in_event_eindpositie)
    overlay_event_properties = 'id8zijde LINE %s %s' % (overlay_event_beginpositie, overlay_event_eindpositie)
    out_event_properties = 'id8zijde LINE %s %s' % (out_event_beginpositie, out_event_eindpositie)
    arcpy.OverlayRouteEvents_lr('in_memory/intable', in_event_properties, 'in_memory/overlaytable', overlay_event_properties,
                                overlay_type, out_table, out_event_properties)


def MaakRowsPerZijde(in_table, zijden):
    # dupliceert records per gevraagde zijde
    NewTable = arcpy.CreateTable_management('in_memory', 'NewTable', in_table)
    arcpy.AddField_management('NewTable', 'zijderijbaan', 'TEXT')
    with arcpy.da.SearchCursor(in_table, '*') as sc:
        with arcpy.da.InsertCursor('NewTable', '*') as ic:
            for row in sc:
                for zijde in zijden:
                    row2 = list(row)
                    row2.append(zijde)
                    row3 = tuple(row2)
                    ic.insertRow(row3)
    return in_table


def VergelijkTabellenADHVattribuut(InputTable1, Veld1, InputTable2, Veld2):
    from arcpy.da import SearchCursor
    # vergelijk tabellen of feature classes op basis van een attribuut.
    # er wordt gekeken of attribuutwaarde bestaat in beide tabellen
    Message = ('VergelijkTabellenADHVattribuut:\n - Parameters: InputTable1: %s, Veld1:%s, InputTable2: %s, Veld2: %s') % (
    str(InputTable1), str(Veld1), str(InputTable2), str(Veld2))
    PrintMessage(Message)
    # Maak lijsten met mogelijke waarden
    WaardenInputTable1 = [str(row[0]) if type(row[0]) == unicode else row[0] for row in SearchCursor(InputTable1, Veld1)]
    WaardenInputTable2 = [str(row[0]) if type(row[0]) == unicode else row[0] for row in SearchCursor(InputTable2, Veld2)]

    # vergelijk de lijsten
    EnkelAanwezigInInputTable1 = list(set(WaardenInputTable1) - set(WaardenInputTable2))
    EnkelAanwezigInInputTable2 = list(set(WaardenInputTable2) - set(WaardenInputTable1))

    return set(EnkelAanwezigInInputTable1), set(EnkelAanwezigInInputTable2)


def MakeValueListForId(Inputtable, idfield, valuefield):
    # aanmaak van een lijst voor de gekozen velden. de lijst bevat meerdere waarden indien de gekozen id meermaals voorkomt in de tabel
    pm.PrintMessage('MakeValueListForId')
    fields = [idfield, valuefield]
    MaxValue = 0
    with arcpy.da.SearchCursor(Inputtable, fields) as sc:
        Result = {}
        for ident, value in sc:
            if ident in Result:
                Result[ident].append(value)
                MaxValue = max(MaxValue, len(Result[ident]))
            else:
                Result[ident] = [value]
        ##            print MaxValue
        Message = 'Max aantal waarden for valuefield = %s' % MaxValue
        pm.PrintMessage(Message)

    return Result, MaxValue


def MaakTableOfFeatureClassFromTxtVeldbeschrijvingen(outputTableFc, txtVeldbeschrijvingen, geometryTypeEsri, hasM, hasZ):
    # maakt een table of featureclass aan op basis van een tekstbestand
    # outputTableFc is workspace en naam van de te maken tabel of featureclass
    # Veldbeschrijving is een list van de te maken velden met hun beschrijving  [[veld1, veldtype, veldlengte],[veld2, veldtype, veldlengte]]
    import os, arcpy
    txtOpenVeldbeschrijvingen = open(txtVeldbeschrijvingen)

    veldbeschrijvingenList = []
    for line in txtOpenVeldbeschrijvingen:
        veldeigenschappen = [veldeigenschap.rstrip('\n').strip() for veldeigenschap in line.split(',')]
        veldbeschrijvingenList.append(veldeigenschappen)

    MaakTableOfFeatureClassFromFieldList(outputTableFc, veldbeschrijvingenList, geometryTypeEsri, hasM, hasZ)


def MaakTableOfFeatureClassFromFieldList(output, veldbeschrijvingenList, geometryTypeEsri, hasM, hasZ):
    import os, arcpy, sys
    PrintMessage('output:%s, veldbeschrijvingenList:%s,geometryTypeEsri:%s, hasM:%s, hasZ:%s' % (
    output, veldbeschrijvingenList, geometryTypeEsri, hasM, hasZ))
    name = os.path.basename(output)
    workspace = os.path.dirname(output)
    if geometryTypeEsri in ('POINT', 'MULTIPOINT', 'POLYLINE', 'POLYGON'):
        spatial_reference = spatial_reference = "PROJCS['Belge_Lambert_1972',GEOGCS['GCS_Belge_1972',DATUM['D_Belge_1972',SPHEROID['International_1924',6378388.0,297.0]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',150000.01256],PARAMETER['False_Northing',5400088.4378],PARAMETER['Central_Meridian',4.367486666666666],PARAMETER['Standard_Parallel_1',49.8333339],PARAMETER['Standard_Parallel_2',51.16666723333333],PARAMETER['Latitude_Of_Origin',90.0],UNIT['Meter',1.0]];-35872700 -30622700 10000;-100000 10000;-100000 10000;0,001;0,001;0,001;IsHighPrecision"
        Message = 'Maak Feature Class: %s' % output;
        PrintMessage(Message)
        Message = 'arcpy.CreateFeatureclass_management(out_path="%s",out_name="%s",geometry_type="%s",template="%s", has_m="%s", has_z="%s",spatial_reference="%s")' % (
        workspace, name, geometryTypeEsri, '#', hasM, hasZ, spatial_reference)
        PrintMessage(Message)
        name = name.replace(" ", "_").replace("(", "_").replace(")", "_")
        layer = arcpy.CreateFeatureclass_management(workspace, name, geometryTypeEsri, '#', hasM, hasZ, spatial_reference)
    else:
        Message = 'Maak Table: %s' % output;
        PrintMessage(Message)
        layer = arcpy.CreateTable_management(workspace, name)

    Message = 'Voeg velden toe: %s' % veldbeschrijvingenList;
    PrintMessage(Message)
    for veld in veldbeschrijvingenList:
        ##        print veld
        ##        PrintMessage(str(veldbeschrijvingenList))
        Message = 'Maak veld %s' % veld;
        PrintMessage(Message)
        ##        PrintMessage (layer+veld[0]+veld[1]+"#"+"#"+veld[2])
        try:
            arcpy.AddField_management(layer, veld[0], veld[1], "#", "#", veld[2])
        except:
            arcpy.AddError(
                'ERROR : (arcpy.AddField_management(%s,%s,%s,%s,%s,%s))' % (layer, veld[0], veld[1], "#", "#", veld[2]))
            sys.exit(0)

    desc = arcpy.Describe(output)
    arcpy.AddMessage('%s aangemaakt als %s' % (output, desc.datasetType))


def HierarchieIdent8(ListIdent8):
    import arcpy
    ##    Message = 'ListIdent8___2:%s' %ListIdent8; arcpy.AddMessage(Message)
    DictIdent8 = {}
    for Ident8 in ListIdent8:

        ##        arcpy.AddMessage('IDENT8888888')
        arcpy.AddMessage(Ident8)
        try:
            Ident8Wegtype = Ident8[0]
            Ident8Wegnummer = int(Ident8[1:4])
            Ident8Index = int(Ident8[4:7])
            Ident8Richting = int(Ident8[-1])
        except:
            Message = 'Fout bij %s:' % Ident8;
            arcpy.AddWarning(Message)
            continue

        WaardeIdent8Index = 600000000

        # 1 *** Waarde volgens wegindex (x1000)
        # Voer eerst een waardebepaling toe a.d.h.v. wegfunctie (inrit, hoofdweg, langsweg,...)

        # hoofdweg
        if Ident8Index in range(901, 927):
            WaardeIdent8Index -= 100000000
        # langswegen (verbinding in-uitritten,...)
        elif Ident8Index in range(500, 520):
            WaardeIdent8Index -= 200000000
        # in-uitritten
        elif Ident8Index in range(11, 500):
            WaardeIdent8Index -= 300000000
        # verbindingsstukken
        elif Ident8Index in range(1, 11):
            WaardeIdent8Index -= 400000000
        # onbelangrijk: bovenbruggen,...
        elif Ident8Index in range(700, 800):
            WaardeIdent8Index -= 500000000
        # overig
        elif Ident8Index > 0:
            WaardeIdent8Index -= 400000000

        # Waardevermindering met index (volgorde in-uitritten,... bepalen
        WaardeIdent8Index -= Ident8Index

        # 2 *** Waarde volgens wegtype
        if Ident8Wegtype == 'R' and Ident8Wegnummer < 10:
            WaardeIdent8Wegtype = 10
        elif Ident8Wegtype == 'A':
            WaardeIdent8Wegtype = 9
        elif Ident8Wegtype == 'B':
            WaardeIdent8Wegtype = 8
        elif Ident8Wegtype == 'R' and Ident8Wegnummer >= 10:
            WaardeIdent8Wegtype = 7
        elif Ident8Wegtype == 'N':
            WaardeIdent8Wegtype = 6
        elif Ident8Wegtype == 'T':
            WaardeIdent8Wegtype = 5

        # 3 *** Waarde volgens wegnummer
        WaardeWegnummer = 1000 - Ident8Wegnummer

        # 4 *** waarde volgens referentierichting richting 1
        WaardeIdent8Richting = 2 - Ident8Richting

        # Totale waarde
        Waarde = (WaardeIdent8Index * 1) + (WaardeIdent8Wegtype * 10000) + (WaardeWegnummer * 10) + WaardeIdent8Richting

        DictIdent8[Ident8] = Waarde

    dictlist = []
    # output list [ident8,waarde]
    for key, value in DictIdent8.iteritems():
        temp = [key, value]
        if temp not in dictlist:
            dictlist.append(temp)
    dictlist.sort(key=lambda x: x[1], reverse=True)
    ListIdent8Waarde = dictlist

    # output gesorteerde ident8
    ListGesorteerdeIdent8 = [value[0] for value in ListIdent8Waarde]

    return ListGesorteerdeIdent8


def Ident7ToIdent8(InputTableOrFc, Ident7Field, OutputTableOrFc):
    import arcpy
    arcpy.AddMessage("OutputTableOrFc = %s" % OutputTableOrFc)
    # maak copy in memory
    arcpy.AddMessage("maak copy in memory")
    if "Table" in str(arcpy.Describe(InputTableOrFc).dataType):
        arcpy.AddMessage("Input is table")
        MemoryTableOrFc = InputTableOrFc = arcpy.CopyRows_management(InputTableOrFc, "in_memory/InputTableOrFc")
    else:
        arcpy.AddMessage("Input is FeatureClass")
        MemoryTableOrFc = InputTableOrFc = arcpy.CopyFeatures_management(InputTableOrFc, "in_memory/InputTableOrFc")

    # voeg ident8 veld voor elke riching toe
    arcpy.AddMessage("Voeg velden toe in memory")
    arcpy.AddField_management(MemoryTableOrFc, "Ident8h1", "TEXT", "#", "#", 8)  # maak veld 'ident8' aan
    arcpy.AddField_management(MemoryTableOrFc, "Ident8h2", "TEXT", "#", "#", 8)  # maak veld 'ident8' aan

    # Calculate ident8 voor beide richtingen
    arcpy.AddMessage("Bereken Ident8 in memory")
    arcpy.CalculateField_management(MemoryTableOrFc, "Ident8h1", "!%s!+'1'" % Ident7Field, "PYTHON_9.3")
    arcpy.CalculateField_management(MemoryTableOrFc, "Ident8h2", "!%s!+'2'" % Ident7Field, "PYTHON_9.3")

    # Split volgens richting
    arcpy.AddMessage("Split per ident8")
    attribute_fields = ";".join([field.name for field in arcpy.ListFields(MemoryTableOrFc)])
    ##    OutputTableOrFc = r'C:\GoogleDrive\SyncGisPcoTeamGis\SyncGisProjecten\onderhoudsprogramma\onderhoudsprogramma202012.gdb\test'
    arcpy.AddMessage("OutputTableOrFc = %s" % OutputTableOrFc)
    arcpy.TransposeFields_management(MemoryTableOrFc, "Ident8h1 Ident8h1;Ident8h2 Ident8h2", OutputTableOrFc, "SourceField",
                                     "Ident8", attribute_fields)

    DeleteFields = ["Ident8h1", "Ident8h2", "SourceField"]
    Message = "Delete fields:%s" % (", ".join(DeleteFields))
    arcpy.AddMessage(Message)
    for Field in DeleteFields:
        arcpy.DeleteField_management(OutputTableOrFc, Field)

    return OutputTableOrFc


def Ident8ToIdent7(InputTableOrFc, Ident8Field, beginpositie, eindpositie, OutputTableOrFc):
    import arcpy, os
    # maak een laag aan per richting met aangepaste veldnamen
    # maak lijst met originele veldnamen, -types, en -lengte
    def maakTable(InputTableOrFc, richting):
        veldOrigineel = [[str(f.name), str(f.type), str(f.length)] for f in arcpy.ListFields(InputTableOrFc) if f.type != "OID"]
        arcpy.AddMessage("veldnamen voor voorlopige laag zijn %s" % str(veldOrigineel))
        for f in veldOrigineel:
            if f[0] == Ident8Field:
                f[0] = "ident7"
                indexIdent8 = veldOrigineel.index(f) + 1
                arcpy.AddMessage("indexIdent8 = %s" % indexIdent8)
            elif f[0] in (beginpositie, eindpositie):
                continue
            else:
                f[0] = f[0] + richting

        ##        arcpy.AddMessage("veldnamen voor voorlopige laag zijn %s" % str(veldOrigineel))

        outputTable = os.path.join("in_memory", os.path.basename(InputTableOrFc + richting))
        arcpy.AddMessage("maak voorlopige laag '%s' aan" % outputTable)
        MaakTableOfFeatureClassFromFieldList(outputTable, veldOrigineel, "table", "", "")

        return indexIdent8, outputTable

    def dataOverzetten(inputTable, outputTable1, outputTable2, indexIdent8):
        arcpy.AddMessage("data overzetten naar tijdelijke lagen")
        # edit sessie starten
        # maak cursors
        workspace = "in_memory"
        arcpy.AddMessage("edit workspace %s" % workspace)
        edit = arcpy.da.Editor(workspace)
        edit.startEditing(True, True)
        edit.startOperation()

        where_clause = "einddatum IS NULL"  # vergelijk enkel met actuele wegsegmenten
        scFields = [f.name for f in arcpy.ListFields(inputTable) if f.type == "OID"] + [f.name for f in
                                                                                        arcpy.ListFields(inputTable) if
                                                                                        f.type != "OID"]
        sc = arcpy.da.SearchCursor(inputTable, scFields)
        arcpy.AddMessage("scFields = %s" % scFields)
        ic1 = arcpy.da.InsertCursor(outputTable1, "*")
        ic2 = arcpy.da.InsertCursor(outputTable2, "*")

        for row in sc:
            row = list(row)
            ##            arcpy.AddMessage("row = %s" % str(row))
            id8_richting = row[indexIdent8][-1]
            ##            arcpy.AddMessage("richting = %s" % richting)
            row[indexIdent8] = row[indexIdent8][:7]

            if id8_richting == "1":
                ic1.insertRow(row)
            elif id8_richting == "2":
                ic2.insertRow(row)
            else:
                arcpy.AddMessage("kan data niet overzetten")
        edit.stopOperation()
        edit.stopEditing(True)

    outputTables = []
    for richting in ("_r1", "_r2"):
        indexIdent8, outputTable = maakTable(InputTableOrFc, richting)
        outputTables.append(outputTable)

    arcpy.AddMessage("outputTables = %s" % str(outputTables))

    dataOverzetten(InputTableOrFc, outputTables[0], outputTables[1], indexIdent8)

    in_event_properties = "%s LINE %s %s" % ("ident7", beginpositie, eindpositie)
    overlay_event_properties = out_event_properties = in_event_properties
    arcpy.OverlayRouteEvents_lr(outputTables[0], in_event_properties, outputTables[1], overlay_event_properties, "UNION",
                                OutputTableOrFc, out_event_properties, "NO_ZERO")


def ToonVerschillenTussen2TabellenOfFc(OrigineleData, GewijzigdeData, CompareFields, VerwijderdeElementenOutput,
                                       NieuweElementenOutput):
    # Zoek wijzigingen tussen 2 tabellen of feature classes en schrijf deze weg naar en nieuwe tabel of fc.
    # Het Idfield moet een unieke waarde bevatten. Deze wordt gebruikt om de elementen met elkaar te vergelijken
    # wijzigingen worden enkel gezocht voor de velden die aanwezig zijn in CompareFields
    ##    from time import strftime
    from arcpy import CreateTable_management, CreateFeatureclass_management
    from arcpy import CopyRows_management, CopyFeatures_management
    from arcpy import da, Describe, env, AddMessage
    import os
    env.overwriteOutput = 'True'

    # maak een lijsten van de originele data en de gewijzigde data
    OrigineleDataList = []
    GewijzigdeDataList = []
    ScFields = CompareFields
    Message = "Maak OrigineleIdList";
    PrintMessage(Message)
    ##    OrigineleIdList = ([row[0] for row in da.SearchCursor(OrigineleData, IdField)])
    OrigineleDataList = ([row for row in da.SearchCursor(OrigineleData, ScFields)])
    Message = "%s  elementen in OrigineleDataList" % len(OrigineleDataList);
    PrintMessage(Message)

    NieuweDataList = []

    list = []
    with da.SearchCursor(GewijzigdeData, ScFields) as Sc:
        for row in Sc:
            if row in OrigineleDataList:
                OrigineleDataList.remove(row)
            ##            if not row in OrigineleDataList:
            ##                [].append(row[0])
            else:
                ##                PrintMessage('Nieuw')
                NieuweDataList.append(row)

    Message = "%s elementen in OrigineleDataList" % len(OrigineleDataList);
    PrintMessage(Message)
    Message = "%s elementen in NieuweDataList" % len(NieuweDataList);
    PrintMessage(Message)

    # Maak Table of Fc voor nieuwe en gewijzigde elementen (terug naar beneden plaatsen)
    for DataList in (NieuweDataList, OrigineleDataList):
        # Outputbestand
        if DataList == OrigineleDataList:
            Output = VerwijderdeElementenOutput
        elif DataList == NieuweDataList:
            Output = NieuweElementenOutput

        # datatype bepalen en outputbestand in memory maken  !!!!!!!! hier zit een fout, er wordt altijd een table gemaaakt!!!!
        if Describe(OrigineleData).dataType == 'FeatureClass':
            AddMessage("maaf fc in memory")
            WsMem = 'in_memory/wijzigingenFc'  # soms faalt deze locatie
            geometry_type = Describe(OrigineleData).shapeType
            ##        Message = "os.path.dirname(WsMem): %s,os.path.basename(WsMem): %s" %(os.path.dirname(WsMem),os.path.basename(WsMem));PrintMessage(Message)
            CreateFeatureclass_management(os.path.dirname(WsMem), os.path.basename(WsMem), geometry_type, OrigineleData)
        else:
            AddMessage("maaf table in memory")
            WsMem = 'in_memory/wijzigingenTable'  # soms faalt deze locatie
            CreateTable_management(os.path.dirname(WsMem), os.path.basename(WsMem), OrigineleData)
        # data schrijven
        Message = "Schrijf data weg naar %s" % WsMem
        with da.InsertCursor(WsMem, ScFields) as Ic:
            for row in DataList:
                Ic.insertRow(row)  # schrijf rij weg naar Wsmem

        if Describe(OrigineleData).dataType == 'FeatureClass':
            CopyFeatures_management(WsMem, Output)
        else:
            CopyRows_management(WsMem, Output)


def ToonWijzigingenTussen2TabellenOfFc(SourceTable, NewTable, IdField, CompareFields, GewijzigdeElementenOutput,
                                       NieuweElementenOutput):
    # Zoek wijzigingen tussen 2 tabellen of feature classes en schrijf deze weg naar en nieuwe tabel of fc.
    # Het Idfield moet een unieke waarde bevatten. Deze wordt gebruikt om de elementen met elkaar te vergelijken
    # wijzigingen worden enkel gezocht voor de velden die aanwezig zijn in CompareFields
    ##    from time import strftime
    from arcpy import CreateTable_management, CreateFeatureclass_management
    from arcpy import CopyRows_management, CopyFeatures_management
    from arcpy import da, Describe, env
    import os
    env.overwriteOutput = 'True'
    WsMem = 'in_memory/wijzigingenTable'  # soms faalt deze locatie

    # Maak een lijst van dictionnary's. Wanneer de waarde van het id-veld  al aanwezig is in een dictionary wordt deze in een volgende of nieuwe gezet
    ScFields = [IdField] + CompareFields
    valueDictList = [{}, ]

    with da.SearchCursor(SourceTable, ScFields) as Sc:
        for r in Sc:
            key = r[0]
            value = r[1:]
            index = 0
            while index < len(valueDictList):
                if key in valueDictList[index]:
                    index += 1
                else:
                    break

            if index < len(valueDictList):
                valueDictList[index][key] = value
            else:
                # id komt in alle bestaande dictionarys voor
                valueDictList.append({key: value})
    ##                PrintMessage('Voeg element toe aan valueDictList')
    for dict in valueDictList:
        Message = "id's die %s keer voorkomen : %s" % (valueDictList.index(dict) + 1, len(dict));
        PrintMessage(Message)

    # Maak Table of Fc voor gewijzigde elementen
    if Describe(SourceTable).dataType == 'FeatureClass':
        WsMem = 'in_memory/wijzigingenFc'  # soms faalt deze locatie
        geometry_type = Describe(SourceTable).shapeType
        ##        Message = "os.path.dirname(WsMem): %s,os.path.basename(WsMem): %s" %(os.path.dirname(WsMem),os.path.basename(WsMem));PrintMessage(Message)
        CreateFeatureclass_management(os.path.dirname(WsMem), os.path.basename(WsMem), geometry_type, SourceTable)
    else:
        WsMem = 'in_memory/wijzigingenTable'  # soms faalt deze locatie
        CreateTable_management(os.path.dirname(WsMem), os.path.basename(WsMem), SourceTable)

    # Maak Table of Fc voor nieue elementen
    if Describe(SourceTable).dataType == 'FeatureClass':
        WsMem = 'in_memory/NieuweElementenFc'  # soms faalt deze locatie
        geometry_type = Describe(SourceTable).shapeType
        CreateFeatureclass_management(os.path.dirname(WsMem), os.path.basename(WsMem), geometry_type, SourceTable)
    else:
        WsMem = 'in_memory/NieuweElementenTable'  # soms faalt deze locatie
        CreateTable_management(os.path.dirname(WsMem), os.path.basename(WsMem), SourceTable)

    # Zoek naar een identiek element in de dictionarys
    FoutenTeller = 0
    IdentiekTeller = 0
    VerschillenIdList = []
    VerwijderdeIdList = []
    NieuweIdList = []
    NieuweDict = {}

    with da.InsertCursor(WsMem, ScFields) as Ic:
        with da.SearchCursor(NewTable, ScFields) as Sc:
            for SearchRow in Sc:
                ##                if FoutenTeller > 100:
                ##                    Message = "stop"; PrintMessage(Message)
                ##                    break
                #
                key = SearchRow[0]
                value = tuple(SearchRow[1:])
                index = 0
                status = ""
                # Find any keyValue that is not in the Dictionary

                while index < len(valueDictList) and status not in (
                "Geen Wijziging", "id niet aanwezig", "id aanwezig maar andere atributen"):
                    valueDict = valueDictList[index]
                    ##                    PrintMessage(index)
                    if key not in valueDict and status == "":  # key komt niet voor in de eerste dict
                        status = "id niet aanwezig"
                    elif key not in valueDict and status == "id aanwezig maar andere atributen, verder zoeken":  # key komt niet voor in 1 van de dict
                        status = "id aanwezig maar andere atributen"
                    elif key in valueDict:  # key bestaat in dict
                        ##                        Message = "key in valuedict"; PrintMessage(Message)
                        if valueDict[key] == value:  # value is gelijk
                            status = "Geen Wijziging"
                        ##                            Message = status; PrintMessage(Message)

                        elif index + 1 < len(
                                valueDictList):  # value is niet gelijk maar mogelijks komt de key voor in volgende dict
                            index += 1
                            status = "id aanwezig maar andere atributen, verder zoeken"
                        #                            Message = "key aanwezig maar andere attributen"; PrintMessage(Message)
                        else:
                            status = "id aanwezig maar andere atributen"

                if status == "id aanwezig maar andere atributen":
                    ##                    Message = "key in valuedict"; PrintMessage(Message)
                    FoutenTeller += 1
                    VerschillenIdList.append(key)
                    row = tuple(SearchRow)
                    Ic.insertRow(row)  # schrijf rij weg naar Wsmem
                elif status == "Geen Wijziging":
                    IdentiekTeller += 1
                elif status == "id niet aanwezig":
                    NieuweIdList.append(key)
                    NieuweDict[key] = value

                else:
                    Message = 'FOUT %s' % key;  # PrintMessage(Message)

    del valueDict
    Message = "\nResultaat van vergelijking";
    PrintMessage(Message)
    Message = "%s identieke elementen" % (IdentiekTeller);
    PrintMessage(Message)
    Message = "%s elementen niet aanwezig in originele tabel (eerste 10): %s" % (len(NieuweIdList), str(NieuweIdList[:10]));
    PrintMessage(Message)
    Message = "%s elementen verschillen (eerste 10): %s" % (len(VerschillenIdList), str(VerschillenIdList[:10]));
    PrintMessage(Message)

    if len(VerschillenIdList) > 0:
        ##        Message =  'Verschillen voor %s id: %s' % (len(VerschillenIdList),str(VerschillenIdList[:10])); PrintMessage(Message)
        if Describe(SourceTable).dataType == 'FeatureClass':
            CopyFeatures_management(WsMem, GewijzigdeElementenOutput)
        else:
            CopyRows_management(WsMem, GewijzigdeElementenOutput)

    if len(NieuweIdList) > 0:
        with da.InsertCursor(WsMem, ScFields) as Ic:
            for key in NieuweDict:

                if Describe(SourceTable).dataType == 'FeatureClass':
                    CopyFeatures_management(WsMem, NieuweElementenOutput)
                else:
                    CopyRows_management(WsMem, NieuweElementenOutput)


def toonVerschillenFieldNames(inputTable0, inputTable1):
    # geeft een lijst terug van velden die voorkomen in inputTable2 maar niet voorkomt in inputTable0
    from arcpy import ListFields
    listFields0 = ListFields(inputTable0)
    listFieldNames0 = [field.name for field in listFields0]
    listFields1 = ListFields(inputTable1)
    listFieldNames1 = [field.name for field in listFields1]

    listVerschillenFieldNames = list(set(listFieldNames1) - set(listFieldNames0))

    return listVerschillenFieldNames


def most_common(inputTable, listFields, resultField):
    # lees de waarden van verschillende velden en schrijf de meest voorkomende waarde weg in een resultatenveld, wanneer er meerdere waarden mogelijk zijn wordt waarde -9 weggeschreven
    import arcpy
    listFields.append(resultField)
    ##    listFields = str(listFields.append(resultField))

    arcpy.AddMessage("listFields=%s" % listFields)
    arcpy.AddMessage("type listFields=%s" % type(listFields))

    with arcpy.da.UpdateCursor(inputTable, listFields) as sC:
        for row in sC:
            countDict = {}
            for value in row:
                if value not in countDict and value != None and value != "":
                    countDict[value] = 1
                elif value != None and value != "":
                    countDict[value] += 1

            ##            arcpy.AddMessage("countDict=%s" %countDict)
            maxKey = max(countDict, key=countDict.get)
            ##            arcpy.AddMessage("maxKey=%s" %maxKey)
            maxValue = countDict[maxKey]

            teller = 0
            for key, value in countDict.items():
                if value == maxValue:
                    teller += 1
            if teller > 1:
                maxKey = -9
            row[-1] = maxKey

            sC.updateRow(row)


def maakGebiedsdekkendEventVanRouteFeatures(inputRouteFeatures, routeIdentifierField, outputEventTable, out_event_properties):
    import os, arcpy, math
    listEvents = []
    maxLengthRouteIdentifier = 0
    typeRouteIdentifierId = "int"
    arcpy.AddMessage("maak Gebiedsdekkend Event Van Route Features (%s)" % inputRouteFeatures)
    arcpy.AddMessage("routeIdentifierField = %s" % routeIdentifierField)
    arcpy.AddMessage(str([field.name for field in (arcpy.ListFields(inputRouteFeatures))]))

    with arcpy.da.SearchCursor(inputRouteFeatures, [routeIdentifierField, "SHAPE@"]) as sC:
        eventId = 0
        for multipartRoute in sC:
            ##            arcpy.AddMessage("multipartRoute = %s" % str(multipartRoute))
            ##            arcpy.AddMessage("type = %s" % type(multipartRoute[0]))

            if type(multipartRoute[0]) == str:
                typeRouteIdentifierId = "text"
                ##                arcpy.AddMessage("type routeidentifier = %s" % type(multipartRoute[0]))
                if len(multipartRoute[0]) == None:
                    arcpy.AddMessage("fout met routeidentifier")
                if len(multipartRoute[0]) > maxLengthRouteIdentifier:
                    maxLengthRouteIdentifier = len(multipartRoute[0])

            for part in multipartRoute[1]:
                listMvalues = [point.M for point in part if not math.isnan(float(point.M))]
                listEvents.append([multipartRoute[0], round(min(listMvalues), 3), round(max(listMvalues), 3), eventId])
                eventId += 1

        arcpy.AddMessage("type routeidentifier = %s" % typeRouteIdentifierId)

    arcpy.CreateTable_management(os.path.dirname(outputEventTable), os.path.basename(outputEventTable))
    out_event_properties_type = ["text", "float", "float"]
    if typeRouteIdentifierId == float:
        out_event_properties_type = ["int", "float", "float"]

    for field in (out_event_properties):
        ##        arcpy.AddMessage("field = %s, out_event_properties = %s" % (field, out_event_properties))
        arcpy.AddField_management(outputEventTable, field, out_event_properties_type[out_event_properties.index(field)], "#", "#",
                                  maxLengthRouteIdentifier)

    # create id field
    arcpy.AddMessage("maak veld 'eventid'")
    arcpy.AddField_management(outputEventTable, "eventId", "LONG")

    insertFields = out_event_properties + ["eventId"]
    ##    arcpy.AddMessage("out_event_properties = %s" %out_event_properties)
    arcpy.AddMessage("insertFields = %s" % insertFields)
    with arcpy.da.InsertCursor(outputEventTable, insertFields) as iC:
        for event in listEvents:
            iC.insertRow(event)


def maakGebiedsdekkendeLaagVanEventTable(inputRouteFeatures, routeIdentifierFieldRouteFeatures, in_event_properties,
                                         inputEventTable, out_table):
    import arcpy
    arcpy.env.overwriteOutput = True

    # maak gebiedsdekkende eventtable
    outputEventTableTemp = "in_memory/gebiedsdekkendEvent"
    maakGebiedsdekkendEventVanRouteFeatures(inputRouteFeatures, routeIdentifierFieldRouteFeatures, outputEventTableTemp,
                                            in_event_properties)
    arcpy.CopyRows_management(outputEventTableTemp, "outputEventTableTemp")  # uitgrijzen

    # maak een gebiedsdekkende laag van inputEventTable
    in_event_properties2list = in_event_properties
    in_event_properties2list.insert(1, "LINE")
    in_event_properties2 = " ".join(in_event_properties2list)
    arcpy.AddMessage("maak Gebiedsdekkend Event Van event table (%s)" % inputEventTable)
    arcpy.AddMessage(
        'arcpy.OverlayRouteEvents_lr(inputEventTable: %s, in_event_properties2: %s, outputEventTableTemp: %s,in_event_properties2 %s, "UNION", out_table: %s, in_event_properties2: %s' % (
        inputEventTable, in_event_properties2, outputEventTableTemp, in_event_properties2, out_table, in_event_properties2))

    arcpy.OverlayRouteEvents_lr(inputEventTable, in_event_properties2, outputEventTableTemp, in_event_properties2, "UNION",
                                out_table, in_event_properties2)


def MaakLengteEvents(inputTable, outputTable, routeId, beginpositie, eindpostie, lengte):
    import arcpy, os, math
    arcpy.AddMessage("maak MaakLengteEvents")
    # naar 25m stukken
    # maak dict met ident8 + begin en eindpositie uit laag inputTable
    dictIdent8_25m = {}
    with arcpy.da.SearchCursor(inputTable, [routeId, beginpositie, eindpostie]) as sc:
        for row in sc:
            beginpositie_sc = round(row[1], 3)
            eindpositie_sc = round(row[2], 3)
            if row[0] not in dictIdent8_25m:
                dictIdent8_25m[row[0]] = [beginpositie_sc, eindpositie_sc]
            elif beginpositie_sc < dictIdent8_25m[row[0]][0]:
                dictIdent8_25m[row[0]] = [beginpositie_sc, dictIdent8_25m[row[0]][1]]
            elif eindpositie_sc > dictIdent8_25m[row[0]][1]:
                dictIdent8_25m[row[0]] = [dictIdent8_25m[row[0]][0], eindpositie_sc]

    # maak tabel met routeid, begin- en eindpositie en een nieuw id, voor routes met gaps zullen niet bestaande events ontstaan
    arcpy.AddMessage("maak tabel %s" % outputTable)
    arcpy.CreateTable_management(os.path.dirname(outputTable), os.path.basename(outputTable))
    arcpy.AddField_management(outputTable, routeId, "TEXT", field_length=8)
    arcpy.AddField_management(outputTable, beginpositie, "FLOAT")
    arcpy.AddField_management(outputTable, eindpostie, "FLOAT")
    arcpy.AddField_management(outputTable, "id25", "TEXT", field_length=30)

    with arcpy.da.InsertCursor(outputTable, [routeId, beginpositie, eindpostie, "id25"]) as ic:
        teller = 0
        for routeId, value in dictIdent8_25m.items():
            start = value[0]
            while start < value[1] and teller < 1000000:
                teller += 1
                stop = (math.floor(round(start / lengte)) * lengte) + lengte
                if stop > value[1]:
                    stop = value[1]
                row = [routeId, start, stop, routeId + "|" + str(round(start, 3)) + "|" + str(round(stop, 3))]
                ic.insertRow(row)
                start = stop


def berekenHoek(bearing1, bearing2):
    # bereken de hoek tussen 2 lijnen met als bron 'bearing' van de lijn
    r = (bearing2 - bearing1) % 360.0
    while r >= 180.0:
        r -= 360.0
    return r


def TestOverlapEvents(inputTable, ident8, beginpositie, eindpositie, zijde, outputtable):
    import arcpy
    ##arcpy.AddMessage('sorteer tabel')
    # sorteer de tabel
    SortFields = [[ident8, "ASCENDING"], [beginpositie, "ASCENDING"], [eindpositie, "ASCENDING"]]  # geen zijde
    if zijde != '': SortFields = [[ident8, "ASCENDING"], [beginpositie, "ASCENDING"], [eindpositie, "ASCENDING"],
                                  [zijde, "ASCENDING"]]
    arcpy.Sort_management(inputTable, "sort", SortFields)

    # voeg veld overlap toe
    arcpy.AddField_management("sort", 'Overlap', 'DOUBLE')

    # indien ident8 gelijk is moet begin van het te controleren record kleiner zijn dan de eindpositie van het vorige record
    arcpy.AddMessage('maak cursor')
    Uc = arcpy.da.UpdateCursor("sort", (ident8, beginpositie, eindpositie, 'Overlap'))
    if zijde != '':
        Uc = arcpy.da.UpdateCursor("sort", (ident8, beginpositie, eindpositie, zijde, 'Overlap'))
    ident8Memory = "ident8Memory"
    zijdeMemory = "zijdeMemory"
    eindpositieMemory = "-999"
    teller = 0
    tellerOverlap = 0

    for event in Uc:
        ##    arcpy.AddMessage(event[0])
        zijdeCurSearch = "zijdeMemory"
        if zijde != '':
            zijdeCurSearch = event[3]
        if ident8Memory == event[0] and zijdeMemory == zijdeCurSearch:
            if eindpositieMemory > round(event[1], 3):  # afronding op 3 cijfers na de comma
                if tellerOverlap < 100:
                    tellerOverlap += 1
                    arcpy.AddMessage("\noverlap voor {0}, {1}, {2}.".format(event[0], event[1], event[2]))
                    arcpy.AddMessage("vorige {0}, {1}".format(ident8Memory, eindpositieMemory))
                    arcpy.AddMessage("lengte {0}".format(eindpositieMemory - event[1]))
                event[-1] = eindpositieMemory
                Uc.updateRow(event)

        ident8Memory = event[0]
        zijdeMemory = zijdeCurSearch
        eindpositieMemory = round(event[2], 3)  # afronding op 3 cijfers na de comma
        ##    arcpy.AddMessage(teller)
        teller += 1
        if teller > 10000000: break

    # resultaten naar output_table
    arcpy.CopyRows_management("sort", outputtable)

    return tellerOverlap


def berekenOverlap(lijnFc, polygoonFc, idField, overlapLengteVeld, overlapPercentageVeld):
    import arcpy, os, datetime
    now = datetime.datetime.now()
    arcpy.AddMessage("start berekening overlap")
    # voeg nodige velden toe
    arcpy.AddField_management(lijnFc, overlapLengteVeld, "FLOAT")
    arcpy.AddField_management(lijnFc, overlapPercentageVeld, "FLOAT")

    # splits de lijnen volgens de polygonenfc
    # selecteer de lijnen die intersecten met polygonen (tijd)
    arcpy.AddMessage(datetime.datetime.now() - now);
    now = datetime.datetime.now()
    arcpy.AddMessage("knip de lijnen op volgens de polygonen")
    arcpy.MakeFeatureLayer_management(lijnFc, 'lijnTemp1')
    arcpy.AddMessage("maak een selectie")
    arcpy.SelectLayerByLocation_management('lijnTemp1', "INTERSECT", polygoonFc)
    arcpy.AddMessage(datetime.datetime.now() - now);
    now = datetime.datetime.now()

    arcpy.AddMessage("knip de lijnen op volgens de polygonen")
    in_features = "lijnTemp1 #;%s #" % (polygoonFc)
    arcpy.Intersect_analysis(in_features, "in_memory/identity1", join_attributes="ALL")
    arcpy.AddMessage(datetime.datetime.now() - now);
    now = datetime.datetime.now()

    # maak een som van de lengtes
    arcpy.AddMessage("maak som van de lengtes per id")
    overlapDict = {}
    with arcpy.da.UpdateCursor("in_memory/identity1", ["WS_OIDN", "shape@LENGTH"]) as sc:
        for row in sc:
            if row[0] in overlapDict:
                overlapDict[row[0]] = overlapDict[row[0]] + row[1]
            else:
                overlapDict[row[0]] = row[1]
    arcpy.AddMessage(datetime.datetime.now() - now);
    now = datetime.datetime.now()

    arcpy.AddMessage("schrijf lengtes weg naar lijnFc")
    with arcpy.da.UpdateCursor(lijnFc, ["WS_OIDN", overlapLengteVeld, overlapPercentageVeld, "Shape_Length"]) as uc:
        for row in uc:
            if row[0] in overlapDict:
                row[1] = overlapDict[row[0]]
                row[2] = round(round(row[1], 3) / round(row[3], 3) * 100, 3)
            else:
                row[1] = 0
                row[2] = 0
            uc.updateRow(row)

    arcpy.AddMessage(datetime.datetime.now() - now);
    now = datetime.datetime.now()


def MaakOpgeknipteEvents(inputTable, event_properties):
    import arcpy
    def MaakLijstVookomendeMeasure(inputTable, event_properties):
        # lijst voorkomende measures op per route
        measures = {}

        arcpy.AddMessage('lijst voorkomende measures op per route (geen rekening houdend met zijde)')
        with arcpy.da.SearchCursor(inputTable, event_properties) as sc:
            for event in sc:
                if event[0] not in measures:
                    measures[event[0]] = [event[1]]
                    measures[event[0]].append(event[2])
                else:
                    if not event[1] in measures[event[0]]:
                        measures[event[0]].append(event[1])
                    if not event[2] in measures[event[0]]:
                        measures[event[0]].append(event[2])

        arcpy.AddMessage(str(measures)[:1000] + ".......")

        return measures

    def MaakGeknipteEventLaag(event_properties, voorkomendeMeasures):
        ident8, beginpositie, eindpositie = event_properties[0], event_properties[1], event_properties[2]
        arcpy.AddMessage('maak nieuwe laag aan met opgelijste measures')
        arcpy.CreateTable_management("in_memory", "knip")
        arcpy.AddField_management("in_memory/knip", ident8, "TEXT", field_length=8)
        arcpy.AddField_management("in_memory/knip", beginpositie, "FLOAT")
        arcpy.AddField_management("in_memory/knip", eindpositie, "FLOAT")
        arcpy.AddField_management("in_memory/knip", "knipId", "LONG")

        with arcpy.da.InsertCursor("in_memory/knip", event_properties + ["knipId"]) as ic:
            knipId = 0
            for route in voorkomendeMeasures:
                ##        arcpy.AddMessage("route = %s" %route)
                routeMeasureSortList = sorted(voorkomendeMeasures[route])
                ##        arcpy.AddMessage(str(routeMeasureSortList))

                for measure in routeMeasureSortList[:-1]:
                    knipId += 1
                    event = [route, measure, routeMeasureSortList[routeMeasureSortList.index(measure) + 1], knipId]
                    try:
                        ic.insertRow(event)
                    except:
                        arcpy.AddError(event)
                        break
        return "in_memory/knip"

    voorkomendeMeasures = MaakLijstVookomendeMeasure(inputTable, event_properties)
    tempEvent = MaakGeknipteEventLaag(event_properties, voorkomendeMeasures)

    return "in_memory/knip"


def JoinField(inputTable, inputJoinField, joinTable, outputJoinField, joinFields):
    import arcpy, sys
    # maak dict van joinFc
    arcpy.AddMessage("maak dict van joinFc")
    fields = [outputJoinField] + joinFields
    joinTableDict = {row[0]: list(row[1:]) for row in arcpy.da.SearchCursor(joinTable, fields)}
    arcpy.AddMessage("joinTableDict = %s" % str(joinTableDict)[:500])

    # maak dict van veldnaam en type van joinTable
    arcpy.AddMessage("maak dict van veldnaam en type van joinTable")
    fieldsInputTableDict = {f.name: [f.type.replace("String", "TEXT"), f.length] for f in arcpy.ListFields(joinTable)}
    arcpy.AddMessage("fieldsInputTableDict = %s" % fieldsInputTableDict)

    # maak velden aan
    arcpy.AddMessage("maak velden aan")
    for f in joinFields:
        try:
            arcpy.AddMessage("reeds aanwezige velden zijn : %s" % str([fi.name for fi in arcpy.ListFields(inputTable)]))
            arcpy.AddMessage(
                "veldnaam = %s, veldtype = %s, veldlengte = %s" % (f, fieldsInputTableDict[f][0], fieldsInputTableDict[f][1]))
            if f in [fi.name for fi in arcpy.ListFields(inputTable)]:
                arcpy.AddError("toe te voegen veld %s is reeds aanwezig in %s")
                sys.exit()
            else:
                arcpy.AddField_management(inputTable, f, fieldsInputTableDict[f][0], "#", "#", fieldsInputTableDict[f][1])
        except:
            arcpy.AddWarning("veld %s niet toegevoegd" % f)
            pass

    # voeg data toe
    fields = [inputJoinField] + joinFields
    with arcpy.da.UpdateCursor(inputTable, fields) as uc:
        for row in uc:
            if row[0] in joinTableDict:
                values = joinTableDict[row[0]]
                ##                arcpy.AddMessage("list = %s" % values)
                rowNew = [row[0]] + list(values)
                ##                arcpy.AddMessage("rowNew = %s" % rowNew)
                uc.updateRow(rowNew)


def JoinFieldMultipleJoinFields(inputTable, inputJoinField, joinTable, outputJoinField, joinFields):
    import arcpy
    # maak dict van joinFc
    fields = outputJoinField + joinFields

    arcpy.AddMessage("inputJoinField = %s" % len(inputJoinField))
    joinTableDict = {row[0:len(inputJoinField)]: list(row[len(inputJoinField):]) for row in
                     arcpy.da.SearchCursor(joinTable, fields)}

    arcpy.AddMessage("joinTableDict = %s" % str(joinTableDict)[:500])

    # maak dict van veldnaam en type van joinTable
    arcpy.AddMessage("maak dict van veldnaam en type van joinTable")
    fieldsInputTableDict = {f.name: [f.type.replace("String", "TEXT"), f.length] for f in arcpy.ListFields(joinTable)}
    arcpy.AddMessage("fieldsInputTableDict = %s" % fieldsInputTableDict)

    # maak velden aan
    arcpy.AddMessage("maak velden aan")
    for f in joinFields:
        try:
            arcpy.AddMessage("reeds aanwezige velden zijn : %s" % str([fi.name for fi in arcpy.ListFields(inputTable)]))
            arcpy.AddMessage(
                "veldnaam = %s, veldtype = %s, veldlengte = %s" % (f, fieldsInputTableDict[f][0], fieldsInputTableDict[f][1]))
            arcpy.AddField_management(inputTable, f, fieldsInputTableDict[f][0], "#", "#", fieldsInputTableDict[f][1])
        except:
            arcpy.AddWarning("veld %s niet toegevoegd" % f)
            pass
    ##
    ##
    # voeg data toe
    fields = inputJoinField + joinFields
    with arcpy.da.UpdateCursor(inputTable, fields) as uc:
        for row in uc:
            if tuple(row[0:len(inputJoinField)]) in joinTableDict:
                ##                arcpy.AddWarning("joinTableDict[tuple(row[0:len(inputJoinField)] )][0:len(inputJoinField)] = %s" % joinTableDict[tuple(row[0:len(inputJoinField)] )][0:len(inputJoinField)])
                values = joinTableDict[tuple(row[0:len(inputJoinField)])][0:len(inputJoinField)]
                ##                arcpy.AddMessage("list = %s" % values)
                rowNew = row[0:len(inputJoinField)] + list(values)
                ##                arcpy.AddMessage("rowNew = %s" % rowNew)
                uc.updateRow(rowNew)
