import requests


class FSConnector:
    def __init__(self, requester):
        self.requester = requester

    def get_raw_lines(self, layer, lines: int = -1) -> object:

        url = f'geolatte-nosqlfs/cert/api/databases/featureserver/{layer}/query'
        if lines > -1:
            url += f'?limit={lines}'
        response = self.requester.get(url)
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
                corrected_el = corrected_el.replace("\\'", "'").replace("\\\\n", " ").replace('\\\\"', "'", ) \
                    .replace(r'\xc2\xb1', '+/-').replace(r'\xc3\xa9', 'é').replace(r'\xe2\x80\x98', "'") \
                    .replace(r'\xe2\x80\x99', "'").replace(r'\xc3\xab', 'ë')
                corrected_list.append(corrected_el)
            return corrected_list
