from datetime import datetime

from OTLMOW.Facility.AssetFactory import AssetFactory
from OTLMOW.OTLModel.Classes.SchokindexVoertuigkering import SchokindexVoertuigkering
from openpyxl import load_workbook

from UploadAfschermendeConstructies.EventDataAC import EventDataAC


class MappingTableProcessor:
    def __init__(self, file_path: str = ''):
        self.mapping_table = []
        self._load_file(file_path)

    def _load_file(self, file_path: str):

        wb = load_workbook(filename=file_path)
        sheet = wb['analyse_afschermende_constructi']

        cells = sheet['A1': 'E188']

        for c1, c2, c3, c4, c5 in cells:
            self.mapping_table.append([c1.value, c2.value, c3.value, c4.value, c5.value])

    def create_otl_object_from_eventDataAC(self, eventDataAC: EventDataAC):
        resultaten = list(
            filter(lambda mappingrecord: mappingrecord[1] == eventDataAC.materiaal and mappingrecord[2] == eventDataAC.product,
                   self.mapping_table))

        if len(resultaten) > 1:
            raise DuplicateMappingError('found more than 1 mapping record')
        elif len(resultaten) == 0:
            raise NotImplementedError('couldn\'t find a mapping record')

        otl_type = resultaten[0][0]

        instance = AssetFactory().dynamic_create_instance_from_name(class_name=str.title(otl_type))

        self.fill_instance(instance, eventDataAC)

        return instance

    def fill_instance(self, instance, eventDataAC):
        instance.geometry = eventDataAC.wktLineStringZM
        if eventDataAC.fabrikant != 'onbekend':
            instance.productidentificatiecode.producent = eventDataAC.fabrikant
        if eventDataAC.opmerking != '':
            instance.notitie = eventDataAC.opmerking
        if eventDataAC.brug != '' and eventDataAC.brug is not None and eventDataAC.brug != 'Nee':
            if instance.notitie is not None:
                instance.notitie += ' - brug:' + eventDataAC.brug
            else:
                instance.notitie = 'brug:' + eventDataAC.brug

        d = datetime.strptime(eventDataAC.begindatum, '%d/%m/%Y')
        instance.datumOprichtingObject = datetime.strptime(eventDataAC.begindatum, '%d/%m/%Y')

        if eventDataAC.schokindex is not None and isinstance(instance, SchokindexVoertuigkering):
            instance.schokindex = str.lower(eventDataAC.schokindex)


class DuplicateMappingError(Exception):
    pass
