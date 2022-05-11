import json

from UploadAfschermendeConstructies.EventDataAC import EventDataAC
from UploadAfschermendeConstructies.WegLocatieData import WegLocatieData


class JsonToEventDataACProcessor:
    def processJsonObjectOrList(self, dict_list, is_list=False):
        if not is_list:
            return self.processJsonObject(dict_list)

        l = []
        for obj in dict_list:
            l.append(self.processJsonObject(obj))
        return l

    def processJsonObject(self, dict_list):
        eventDataAC = EventDataAC()
        eventDataAC.ident8 = dict_list["properties"]["ident8"]
        eventDataAC.wktLineStringZM = self.FSInputToWktLineStringZM(dict_list["geometry"]["coordinates"])
        eventDataAC.begin = WegLocatieData()
        eventDataAC.begin.positie = dict_list["properties"]["locatie"]["begin"]["positie"]
        eventDataAC.begin.bron = dict_list["properties"]["locatie"]["begin"]["bron"]
        eventDataAC.begin.wktPoint = self.FSInputToWktPoint(
            dict_list["properties"]["locatie"]["begin"]["geometry"]["coordinates"])
        eventDataAC.eind = WegLocatieData()
        eventDataAC.eind.positie = dict_list["properties"]["locatie"]["eind"]["positie"]
        eventDataAC.eind.bron = dict_list["properties"]["locatie"]["eind"]["bron"]
        eventDataAC.eind.wktPoint = self.FSInputToWktPoint(dict_list["properties"]["locatie"]["eind"]["geometry"]["coordinates"])
        eventDataAC.product = dict_list["properties"]["product"]
        eventDataAC.typeAC = dict_list["properties"]["type"]
        eventDataAC.materiaal = dict_list["properties"]["materiaal"]
        eventDataAC.fabrikant = dict_list["properties"]["fabrikant"]
        eventDataAC.opmerking = dict_list["properties"]["opmerking"]
        eventDataAC.brug = dict_list["properties"]["brug"]
        eventDataAC.begindatum = dict_list["properties"]["begindatum"]
        eventDataAC.gebied = dict_list["properties"]["gebied"]
        eventDataAC.schokindex = dict_list["properties"]["schokindex"]

        eventDataAC.zijde_rijbaan = dict_list["properties"]["zijderijbaan"]
        afstand_rijbaan = dict_list["properties"]["afstandrijbaan"]
        if afstand_rijbaan is not None:
            eventDataAC.afstand_rijbaan = afstand_rijbaan / 100.0

        return eventDataAC

    def processJson(self, jsonList) -> [EventDataAC]:
        returnlist = []

        for el in jsonList:
            dict_list = json.loads(el.replace('\n', ''))
            eventDataAC = self.processJsonObjectOrList(dict_list)
            returnlist.append(eventDataAC)

        return returnlist

    def FSInputToWktLineStringZM(self, FSInput):
        s = 'LINESTRING ZM ('
        for punt in FSInput:
            for fl in punt:
                s += str(fl) + ' '
            s = s[:-1] + ', '
        s = s[:-2] + ')'
        return s

    def FSInputToWktPoint(self, FSInput):
        s = ' '.join(list(map(str, FSInput)))
        return f'POINT ({s})'

