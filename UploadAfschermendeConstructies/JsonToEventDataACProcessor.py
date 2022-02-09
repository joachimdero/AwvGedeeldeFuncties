import json

from UploadAfschermendeConstructies.EventDataAC import EventDataAC
from UploadAfschermendeConstructies.WegLocatieData import WegLocatieData


class JsonToEventDataACProcessor:
    def processJson(self, jsonList) -> []:
        returnlist = []

        for el in jsonList:
            dict_list = json.loads(el.replace('\n', ''))
            eventDataAC = EventDataAC()
            eventDataAC.ident8 = dict_list["properties"]["ident8"]
            eventDataAC.wktLineStringZM = self.FSInputToWktLineStringZM(dict_list["geometry"]["coordinates"])
            eventDataAC.begin = WegLocatieData()
            eventDataAC.begin.positie = dict_list["properties"]["locatie"]["begin"]["positie"]
            eventDataAC.begin.bron = dict_list["properties"]["locatie"]["begin"]["bron"]
            eventDataAC.begin.wktPoint = self.FSInputToWktPoint(dict_list["properties"]["locatie"]["begin"]["geometry"]["coordinates"])
            eventDataAC.eind = WegLocatieData()
            eventDataAC.eind.positie = dict_list["properties"]["locatie"]["eind"]["positie"]
            eventDataAC.eind.bron = dict_list["properties"]["locatie"]["eind"]["bron"]
            eventDataAC.eind.wktPoint = self.FSInputToWktPoint(dict_list["properties"]["locatie"]["eind"]["geometry"]["coordinates"])
            eventDataAC.product = self.FSInputToWktPoint(dict_list["properties"]["product"])
            eventDataAC.typeAC = self.FSInputToWktPoint(dict_list["properties"]["type"])

            eventDataAC.zijde_rijbaan = dict_list["properties"]["zijderijbaan"]
            afstand_rijbaan = dict_list["properties"]["afstandrijbaan"]
            if afstand_rijbaan is not None:
                eventDataAC.afstand_rijbaan = afstand_rijbaan / 100.0

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

