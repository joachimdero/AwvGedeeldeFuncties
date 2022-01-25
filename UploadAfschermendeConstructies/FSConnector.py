import requests


class FSConnector:
    def get_raw_lines(self, layer, lines):
        cert_path = 'C:\\resources\\datamanager_eminfra_prd.awv.vlaanderen.be.crt'
        key_path = 'C:\\resources\\datamanager_eminfra_prd.awv.vlaanderen.be.key'
        url = f'https://services.apps.mow.vlaanderen.be/geolatte-nosqlfs/cert/api/databases/featureserver/{layer}/query?limit={lines}'
        response = requests.get(url, cert=(cert_path, key_path))
        if response.status_code == 200:

            raw_string = str(response.content)
            raw_string = raw_string[2:-2]

            corrected_list = []
            splitted_list = raw_string.split('}\\n{')
            for el in splitted_list:
                corrected_el = '{' + el + '}'
                if el == splitted_list[0]:
                    corrected_el = corrected_el[1:]
                elif el == splitted_list[-1]:
                    corrected_el = corrected_el[:-2]
                corrected_list.append(corrected_el)
            return corrected_list