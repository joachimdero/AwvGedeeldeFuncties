import requests


class FSConnector:
    def get_raw_lines(self, layer, cert_path: str,key_path: str, lines: int=-1):

        url = f'https://services.apps.mow.vlaanderen.be/geolatte-nosqlfs/cert/api/databases/featureserver/{layer}/query'
        if lines > -1:
            url += f'?limit={lines}'
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
                corrected_el = corrected_el.replace("\\'", "'").replace("\\\\n", " ").replace('\\\\"', "'", ) \
                    .replace(r'\xc2\xb1', '+/-').replace(r'\xc3\xa9', 'é').replace(r'\xe2\x80\x98', "'") \
                    .replace(r'\xe2\x80\x99', "'").replace(r'\xc3\xab', 'ë')
            return corrected_list