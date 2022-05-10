from unittest import TestCase


class WKT_Simplifier:
    @classmethod
    def correct_zm_string_to_z_string(cls, teststring: str):
        parts = teststring.split('((')
        wkt_type = parts[0].replace('M ', ' ')
        numbers_string = parts[1].split('))')[0]
        numbers_array = numbers_string.split(', ')
        new_array = []
        for point in numbers_array:
            coords = point.split(' ')
            new_array.append(' '.join(coords[0:3]))
        wkt = wkt_type + '((' + ', '.join(new_array) + '))'
        return wkt


class WKT_SimplifierTests(TestCase):
    def test_MultilineZM(self):
        teststring = 'MULTILINESTRING ZM ((103333.63404978078 191928.96019978262 5.7255458645522594 NAN, 103332.98739755852 191928.97025321238 5.6865532780066133 NAN))'
        result = WKT_Simplifier.correct_zm_string_to_z_string(teststring)
        expected = 'MULTILINESTRING Z ((103333.63404978078 191928.96019978262 5.7255458645522594, 103332.98739755852 191928.97025321238 5.6865532780066133))'
        self.assertEqual(result, expected)