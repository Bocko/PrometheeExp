from math import exp

class PreferenceType2:
    q = 0
    def __init__(self, valQ):
        self.q = valQ
    def value(self, diff):
        if (diff <= self.q):
            return 0
        return 1

class PreferenceType5:
    q = 0
    p = 1
    def __init__(self, valQ, valP):
        self.q = valQ
        self.p = valP
    def value(self, diff):
        if (diff <= self.q):
            return 0
        if (diff <= self.p):
            return (diff - self.q) / (self.p - self.q)
        return 1

class PreferenceType6:
    s = 0.5
    valSquare = 0.5
    def __init__(self, valS):
        self.s = valS
        self.valSquare = -1 * (2 * valS * valS)
    def value(self, diff):
        if (diff <= 0):
            return 0
        return 1 - exp(diff * diff / self.valSquare)