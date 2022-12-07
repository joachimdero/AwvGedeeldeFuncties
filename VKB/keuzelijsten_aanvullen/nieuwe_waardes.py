import rdflib
from rdflib import Graph, URIRef, RDF

if __name__ == '__main__':
    f = open("input.csv", "r")
    lines = f.read().split('\n')
    codes = set()
    for line in lines:
        codes.update(set(line.split(' ')))

    g = Graph()
    g.parse("KlVerkeersbordCode.ttl")

    existing = []
    for o in g.objects():
        if not str(o).startswith('http'):
            existing.append(str(o))

    existing_codes = list(set(existing))

    with open('vkl_aanvullingen.ttl', 'w') as writer:
        for code in codes:
            if code in existing_codes:
                continue
            if code[0] not in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'M']:
                print('found')
                continue
            template_lines = ['<https://wegenenverkeer.data.vlaanderen.be/id/concept/KlVerkeersbordCode/F67> a skos:Concept;\n',
'<https://www.w3.org/ns/adms#status> <https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAdmsStatus/ingebruik>;\n',
'  skos:definition "F67"@nl;\n',
'  skos:inScheme <https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlVerkeersbordCode>;\n',
'  skos:notation "F67";\n',
'  skos:prefLabel "F67"@nl;\n',
'  skos:topConceptOf <https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlVerkeersbordCode> .\n', '\n']
            added_ttl = []
            for line in template_lines:
                added_ttl.append(line.replace('F67', code))

            writer.writelines(added_ttl)



    print(codes)
