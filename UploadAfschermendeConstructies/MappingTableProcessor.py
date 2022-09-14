from datetime import datetime

from OTLMOW.Facility.AssetFactory import AssetFactory
from OTLMOW.OTLModel.Classes.Abstracten.SchokindexVoertuigkering import SchokindexVoertuigkering
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

    def create_otl_objects_from_eventDataAC(self, eventDataAC: EventDataAC) -> []:
        resultaten = list(
            filter(lambda mappingrecord: mappingrecord[2] == eventDataAC.product,
                   self.mapping_table))

        if len(resultaten) > 1:
            raise DuplicateMappingError('found more than 1 mapping record')
        elif len(resultaten) == 0:
            raise NotImplementedError('couldn\'t find a mapping record')

        otl_type = resultaten[0][0]
        instance_list = []

        if '/' in otl_type:
            for otl_type in otl_type.split('/'):
                instance = AssetFactory().dynamic_create_instance_from_ns_and_name(namespace='onderdeel',
                                                                                   class_name=str.title(otl_type).replace(' ', ''))

                if instance is not None:
                    if instance.materiaal is not None and not instance.materiaal.starts_with('beton'):
                        instance.materiaal = resultaten[0][1]
                    self.fill_instance(instance=instance, eventDataAC=eventDataAC)
                    instance_list.append(instance)
        else:
            instance = AssetFactory().dynamic_create_instance_from_ns_and_name(namespace='onderdeel',
                                                                               class_name=str.title(otl_type).replace(' ', ''))

            if instance is not None:
                if instance.materiaal is not None and not instance.materiaal.starts_with('beton'):
                    instance.materiaal = resultaten[0][1]
                self.fill_instance(instance=instance, eventDataAC=eventDataAC)
                instance_list.append(instance)

        return instance_list

    @staticmethod
    def fill_instance(instance, eventDataAC):
        instance.geometry = eventDataAC.offset_wkt
        if eventDataAC.fabrikant != 'onbekend':
            instance.productidentificatiecode.producent = eventDataAC.fabrikant
        if eventDataAC.opmerking != '':
            instance.notitie = eventDataAC.opmerking
        if eventDataAC.brug != '' and eventDataAC.brug is not None and eventDataAC.brug != 'Nee':
            if instance.notitie is not None:
                instance.notitie += ' - brug:' + eventDataAC.brug
            else:
                instance.notitie = 'brug:' + eventDataAC.brug

        dt = datetime.strptime(eventDataAC.begindatum, '%d/%m/%Y')
        d = datetime.date(dt)
        instance.datumOprichtingObject = d

        if eventDataAC.schokindex is not None and isinstance(instance, SchokindexVoertuigkering):
            instance.schokindex = str.lower(eventDataAC.schokindex)


class DuplicateMappingError(Exception):
    pass
