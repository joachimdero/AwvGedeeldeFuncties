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
        sheet = wb['mapping']

        cells = sheet['A2': 'H153']

        for c1, c2, c3, c4, c5, c6, c7, c8 in cells:
            self.mapping_table.append([c1.value, c2.value, c3.value, c4.value, c5.value, c6.value, c7.value, c8.value])

    def create_otl_objects_from_eventDataAC(self, eventDataAC: EventDataAC) -> []:
        resultaten = list(
            filter(lambda mappingrecord: mappingrecord[0] == eventDataAC.product,
                   self.mapping_table))

        if len(resultaten) > 1:
            raise DuplicateMappingError('found more than 1 mapping record')
        elif len(resultaten) == 0:
            raise NotImplementedError('couldn\'t find a mapping record')

        resultaat_mapping = resultaten[0]
        instance_list = []
        otl_type = resultaat_mapping[2]

        if resultaat_mapping[3] is not None and 'en' in resultaat_mapping[3]:
            instance = AssetFactory().dynamic_create_instance_from_ns_and_name(namespace='onderdeel',
                                                                               class_name=str.title(otl_type).replace(' ', ''))
            instance_list.append(instance)
            instance = AssetFactory().dynamic_create_instance_from_ns_and_name(namespace='onderdeel',
                                                                               class_name=str.title(resultaat_mapping[4]).replace(
                                                                                   ' ', ''))
            instance_list.append(instance)
        elif resultaat_mapping[3] is not None and 'of' in resultaat_mapping[3]:
            instance = AssetFactory().dynamic_create_instance_from_ns_and_name(namespace='onderdeel',
                                                                               class_name=str.title(resultaat_mapping[4]).replace(
                                                                                   ' ', ''))
            instance_list.append(instance)
        else:
            instance = AssetFactory().dynamic_create_instance_from_ns_and_name(namespace='onderdeel',
                                                                               class_name=str.title(otl_type).replace(' ', ''))
            if instance is not None:
                instance_list.append(instance)

        for instance in instance_list:
            if instance.materiaal is not None and not instance.materiaal.starts_with('beton'):
                instance.materiaal = resultaat_mapping[5]
            if resultaat_mapping[7] is not None and str(resultaat_mapping[7]) != 'None':
                instance.productidentificatiecode.productidentificatiecode = resultaat_mapping[7]
            self.fill_instance(instance=instance, eventDataAC=eventDataAC)

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

        if eventDataAC.schokindex != '' and eventDataAC.schokindex is not None and isinstance(instance, SchokindexVoertuigkering):
            instance.schokindex = str.lower(eventDataAC.schokindex)


class DuplicateMappingError(Exception):
    pass
