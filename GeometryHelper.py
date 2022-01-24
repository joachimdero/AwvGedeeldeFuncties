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

    @staticmethod    
    def find_min_buffersize_from_geometry_to_be_within_another(geometry: BaseGeometry, within_geometry: BaseGeometry,
                                                               buffer: float = 1, buffer_step: float = 1,
                                                               step: int = 5, round_to: int = -5) -> float:
        """Calculates the minimum buffer to draw around geometry (2) to have geometry (1) be completely within
    
        :param geometry: The first geometry, that will be checked to be within another.
        :type geometry: shapely.BaseGeometry
        :param within_geometry: The second geometry, that will be used to draw a buffer around and check if the first geometry is within.
        :type within_geometry: shapely.BaseGeometry
        :param buffer: The buffer size's starting value. This should be an estimate of the expected value, defaults to 1
        :type buffer: float
        :param buffer_step: The buffer_step starting value. The algorithm uses steps of this size to find the optimal value for buffer, defaults to 1
        :type buffer_step: float
        :param step: The amount of steps will be taken, starting from buffer and multiplied by buffer_step to check per iteration, defaults to 5.
        :type buffer_step: int
        :param round_to: The result will be round to 10 to the power of this value, i.e. -3 will round the result to 0.001, defaults to -5
        :type buffer_step: int
        :rtype: float
        :return: returns the result of the algorithm"""
    
        if abs(buffer_step) < 10 ** (round_to-1):
            return round(buffer, -round_to)
        if geometry.within(within_geometry.buffer(buffer)):
            # go down
            for i in range(step + 2):
                new_buffer = buffer + buffer_step * i
                within = geometry.within(within_geometry.buffer(new_buffer))
                if not within:
                    new_i = i
                    break
            return find_min_buffersize_from_geometry_to_be_within_another(geometry, within_geometry, buffer + buffer_step * new_i,
                                                                          -buffer_step / step, step, round_to)
        else:
            # go up
            for i in range(step + 2):
                new_buffer = buffer + buffer_step * i
                within = geometry.within(within_geometry.buffer(new_buffer))
                if within:
                    new_i = i
                    break
            return find_min_buffersize_from_geometry_to_be_within_another(geometry, within_geometry, buffer + buffer_step * new_i,
                                                                          -buffer_step / step, step, round_to)
