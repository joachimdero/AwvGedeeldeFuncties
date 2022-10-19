from datetime import datetime

from openpyxl import load_workbook
from otlmow_converter.AssetFactory import AssetFactory
from otlmow_model.Classes.Abstracten.SchokindexVoertuigkering import SchokindexVoertuigkering

from UploadAfschermendeConstructies.EventDataAC import EventDataAC


class RijbaanMappingTableProcessor:
    def __init__(self, file_path: str = ''):
        self.mapping_table = {}
        self._load_file(file_path)

    def _load_file(self, file_path: str):

        wb = load_workbook(filename=file_path)
        sheet = wb['Sheet1']

        cells = sheet['A2': 'C50']

        for c1, c2, c3 in cells:
            if c1.value is None:
                c1.value = ''
            self.mapping_table[(c1.value.strip(), c2.value)] = c3.value
