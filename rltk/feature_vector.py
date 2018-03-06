class FeatureVector:
    _data_1 = None
    _data_2 = None
    _similarity_result = None
    value = None

    def __init__(self, data_1, data_2):
        self._data_1 = data_1
        self._data_2 = data_2

        self._similarity_result = []
        self.value = 0

    def add_similiairy(self, feature_function, **kwargs):
        value_list = []
        for key in self._data_1[1]:
            if key == 'id':
                continue
            if key in self._data_2[1]:
                value = feature_function(self._data_1[1][key], self._data_2[1][key], kwargs)
                self.add(value)
                value_list.append(value)

        return value_list

    def add_similiairy_byid(self, col_1, col_2, feature_function, **kwargs):
        self.value = feature_function(self._data_1[1][col_1], self._data_2[1][col_2], kwargs)
        self.add(self.value)
        return self.value

    def add(self, value):
        self.value = value
        self._similarity_result.append(self.value)
        return self.value

    def compute_prob(self):
        return self.value
