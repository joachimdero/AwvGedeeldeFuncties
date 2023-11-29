import json
import platform

import pandas as pd

from FSConnector import FSConnector
from UploadAfschermendeConstructies.OTLMOW_Helpers.RequesterFactory import RequesterFactory
from UploadAfschermendeConstructies.SettingsManager import SettingsManager

if __name__ == '__main__':
    # if platform.system() == 'Linux':
    #     OTLMOW_settings_path = '/home/davidlinux/Documents/AWV/resources/settings_OTLMOW.json'
    #     this_settings_path = 'settings_OTLMOW_linux.json'
    # else:
    #     OTLMOW_settings_path = 'C:\\resources\\settings_OTLMOW.json'
    #     this_settings_path = 'C:\\resources\\settings_AWVGedeeldeFuncties.json'
    #
    # # een aantal classes uit OTLMOW library gebruiken
    # settings_manager = SettingsManager(settings_path=this_settings_path)
    # requester = RequesterFactory.create_requester(settings=settings_manager.settings, auth_type='cert', env='prd')
    #
    # fs_c = FSConnector(requester)
    #
    # raw_output = fs_c.get_raw_lines(layer="afschermendeconstructies")
    #
    # with open("AC.json", "w") as f:
    #     f.write('[' + ',\n'.join(raw_output) + ']')

    # with open('AC.json') as json_file:
    #     raw_output = json_file.readlines()
    #     dict_list = []
    #     for el in raw_output:
    #         dict_list.append(json.loads(el.replace('\n', '')))
    # df = pd.json_normalize(dict_list)

    with open('AC.json') as json_file:
        data = json.load(json_file)
    df = pd.json_normalize(data)

    pd.set_option('display.max_rows', None)
    print(df.dtypes)
    df.to_csv('analyse_pandas_AC.csv', sep='\t')

    df_grouped = df.groupby(['properties.type', 'properties.materiaal', 'properties.product', 'properties.fabrikant'], dropna=False).size()
    df_grouped.to_csv('analyse_afschermende_constructies.csv', sep='\t')

    #print(df['properties.type'].value_counts())

    pass

#  te bekijken naast https://docs.google.com/spreadsheets/d/1C0pfa-ntBvqVn2DLNtBJst-fCZGXjX-7/edit#gid=2055843188