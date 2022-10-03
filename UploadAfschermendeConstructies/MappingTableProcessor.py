from datetime import datetime

from openpyxl import load_workbook
from otlmow_converter.AssetFactory import AssetFactory
from otlmow_model.Classes.Abstracten.SchokindexVoertuigkering import SchokindexVoertuigkering

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
        resultaat_mapping = self.find_mapping_record_based_on_product(eventDataAC.product)

        instance_list = []
        otl_type = resultaat_mapping[2]

        if resultaat_mapping[3] is not None and 'en' in resultaat_mapping[3]:
            instance = AssetFactory.dynamic_create_instance_from_ns_and_name(namespace='onderdeel',
                                                                               class_name=self.get_class_name(otl_type))
            instance_list.append(instance)
            instance.assetId.identificator = eventDataAC.id + '_1'
            instance2 = AssetFactory.dynamic_create_instance_from_ns_and_name(namespace='onderdeel',
                                                                                class_name=self.get_class_name(
                                                                                    resultaat_mapping[4]))
            instance_list.append(instance2)
            instance2.assetId.identificator = eventDataAC.id + '_2'
        elif resultaat_mapping[3] is not None and 'of' in resultaat_mapping[3]:
            instance = AssetFactory.dynamic_create_instance_from_ns_and_name(namespace='onderdeel',
                                                                               class_name=self.get_class_name(
                                                                                   resultaat_mapping[4]))
            instance_list.append(instance)
            instance.assetId.identificator = eventDataAC.id
        else:
            instance = AssetFactory.dynamic_create_instance_from_ns_and_name(namespace='onderdeel',
                                                                               class_name=self.get_class_name(otl_type))
            if instance is not None:
                instance_list.append(instance)
            instance.assetId.identificator = eventDataAC.id

        for instance in instance_list:
            instance.assetId.toegekendDoor = 'UploadAfschermendeConstructies'

            if instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#SchampkantStd':
                if resultaat_mapping[5] == 'beton':
                    instance.soort = 'betonnen schampkant'
            else:
                if resultaat_mapping[5] == 'in situ beton':
                    instance.materiaal = 'in-situ-beton'
                elif resultaat_mapping[5] == 'geprefabriceerde beton':
                    instance.materiaal = 'geprefabriceerde-beton'
                else:
                    instance.materiaal = resultaat_mapping[5]

                if resultaat_mapping[7] is not None and str(resultaat_mapping[7]) != 'None':
                    instance.productidentificatiecode.productidentificatiecode = resultaat_mapping[7]

            MappingTableProcessor.fill_instance(instance=instance, eventDataAC=eventDataAC)

        return instance_list

    @staticmethod
    def fill_instance(instance, eventDataAC):
        instance.geometry = eventDataAC.offset_wkt
        if eventDataAC.fabrikant != 'onbekend' and instance.typeURI != 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#SchampkantStd':
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

        if eventDataAC.schokindex != '' and eventDataAC.schokindex is not None and isinstance(instance,
                                                                                              SchokindexVoertuigkering):
            instance.schokindex = str.lower(eventDataAC.schokindex)

    @staticmethod
    def get_class_name(otl_type):
        otl_type = str.title(otl_type).replace(' ', '')
        if otl_type == 'GestandaardiseerdeSchampkant':
            return 'SchampkantStd'
        return otl_type

    def find_mapping_record_based_on_product(self, product):
        resultaten = list(filter(lambda mappingrecord: mappingrecord[0] == product,
                                 self.mapping_table))

        if len(resultaten) > 1:
            raise DuplicateMappingError('found more than 1 mapping record')
        elif len(resultaten) == 0:
            if product.strip() != product:
                return self.find_mapping_record_based_on_product(product.strip())
            raise NotImplementedError('could not find a mapping record')

        return resultaten[0]


class DuplicateMappingError(Exception):
    pass
