class GeometryHelper:
    @staticmethod
    def bereken_hoek(a, b):
        """bereken de hoek tussen 2 lijnen met als bron 'bearing' van de lijn"""
        if None in (a,b):
            raise ValueError("None is geen geldige waarde")
        r = (b-a) % 360.0
        if r >= 180.0:
            r -= 360.0
        if r < -180.0:
            r += 360.0
        return r