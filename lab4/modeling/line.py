# 2016 (C) Valentin Lukyanets, SCSm-16-1


from logic_value import LogicValue


class Line:
    def __init__(self):
        self.driver = None
        self.drivens = []
        self.value = LogicValue.FALSE

    def propagate(self):
        self.value = self.driver().value
        for driven in self.drivens:
            driven().value = self.value
