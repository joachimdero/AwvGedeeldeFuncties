import json

import pandas as pd

from FSConnector import FSConnector

if __name__ == '__main__':
    # fs_c = FSConnector()
    # cert_path = r'C:\resources\datamanager_eminfra_prd.awv.vlaanderen.be.crt'
    # key_path = r'C:\resources\datamanager_eminfra_prd.awv.vlaanderen.be.key'
    # raw_output = fs_c.get_raw_lines(layer="afschermendeconstructies",
    #                                 cert_path=cert_path,
    #                                 key_path=key_path)
    #
    # f = open("demofile.json", "w")
    # f.write('[' + ',\n'.join(raw_output) + ']')
    # f.close()
    #

    # df = pd.read_json('demofile.json')

    with open('AC.json') as json_file:
        raw_output = json_file.readlines()
        dict_list = []
        for el in raw_output:
            dict_list.append(json.loads(el.replace('\n', '')))
    df = pd.json_normalize(dict_list)

    pd.set_option('display.max_rows', None)
    print(df.dtypes)
    df.to_csv('analyse_pandas_AC.csv', sep='\t')

    df_grouped = df.groupby(['properties.type', 'properties.materiaal', 'properties.product', 'properties.fabrikant'], dropna=False).size()
    df_grouped.to_csv('analyse_afschermende_constructies.csv', sep='\t')

    #print(df['properties.type'].value_counts())

    pass

#  te bekijken naast https://docs.google.com/spreadsheets/d/1C0pfa-ntBvqVn2DLNtBJst-fCZGXjX-7/edit#gid=2055843188