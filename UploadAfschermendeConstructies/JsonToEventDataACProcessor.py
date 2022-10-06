import json

from UploadAfschermendeConstructies.EventRijbaan import EventRijbaan
from UploadAfschermendeConstructies.EventDataAC import EventDataAC
from UploadAfschermendeConstructies.WegLocatieData import WegLocatieData


class JsonToEventDataACProcessor:
    def process_json_object_or_list_ac(self, dict_list, is_list=False):
        if not is_list:
            return self.process_json_to_event_data_ac(dict_list)

        l = []
        for obj in dict_list:
            l.append(self.process_json_to_event_data_ac(obj))
        return l

    def process_json_to_event_data_ac(self, dict_list):
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
        if "gebied" in dict_list["properties"]:
            eventDataAC.gebied = dict_list["properties"]["gebied"]
        eventDataAC.schokindex = dict_list["properties"]["schokindex"]
        eventDataAC.id = dict_list["properties"]["id"]

        eventDataAC.zijde_rijbaan = dict_list["properties"]["zijderijbaan"]
        afstand_rijbaan = dict_list["properties"]["afstandrijbaan"]
        if afstand_rijbaan is not None:
            eventDataAC.afstand_rijbaan = afstand_rijbaan / 100.0

        return eventDataAC

    def process_json_to_list_event_data_ac(self, jsonList) -> [EventDataAC]:
        returnlist = []

        for el in jsonList:
            dict_list = json.loads(el.replace('\n', ''))
            event_data_ac = self.process_json_object_or_list_ac(dict_list)
            returnlist.append(event_data_ac)

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

    def process_json_to_list_event_rijbaan(self, jsonList) -> [EventRijbaan]:
        returnlist = []

        for el in jsonList:
            dict_list = json.loads(el.replace('\n', ''))
            event_rijbaan = self.process_json_object_or_list_rb(dict_list)
            returnlist.append(event_rijbaan)

        return returnlist

    def process_json_object_or_list_rb(self, dict_list, is_list=False):
        if not is_list:
            return self.process_json_to_event_rijbaan(dict_list)

        l = []
        for obj in dict_list:
            l.append(self.process_json_to_event_rijbaan(obj))
        return l

    def process_json_to_event_rijbaan(self, dict_list):
        event_rijbaan = EventRijbaan()
        event_rijbaan.wegcategorie = dict_list["properties"].get("wegcategorie", '')
        event_rijbaan.ident8 = dict_list["properties"]["ident8"]
        event_rijbaan.aantal_rijstroken = dict_list["properties"]["aantalrijstroken"]
        event_rijbaan.rijrichting = dict_list["properties"]["rijrichting"]
        event_rijbaan.id = dict_list["properties"]["id"]
        event_rijbaan.breedte_rijbaan = dict_list["properties"]["breedterijbaan"]
        event_rijbaan.opmerking = dict_list["properties"]["opmerking"]
        event_rijbaan.wktLineStringZM = self.FSInputToWktLineStringZM(dict_list["geometry"]["coordinates"])
        event_rijbaan.begin = WegLocatieData()
        event_rijbaan.begin.positie = dict_list["properties"]["locatie"]["begin"]["positie"]
        event_rijbaan.begin.bron = dict_list["properties"]["locatie"]["begin"]["bron"]
        event_rijbaan.begin.wktPoint = self.FSInputToWktPoint(
            dict_list["properties"]["locatie"]["begin"]["geometry"]["coordinates"])
        event_rijbaan.eind = WegLocatieData()
        event_rijbaan.eind.positie = dict_list["properties"]["locatie"]["eind"]["positie"]
        event_rijbaan.eind.bron = dict_list["properties"]["locatie"]["eind"]["bron"]
        event_rijbaan.eind.wktPoint = self.FSInputToWktPoint(dict_list["properties"]["locatie"]["eind"]["geometry"]["coordinates"])

        return event_rijbaan
