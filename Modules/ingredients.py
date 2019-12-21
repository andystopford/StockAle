class Grain:
    def __init__(self, name, EBC, extr, wgt):
        self.name = name
        self.ebc = EBC
        self.extr = extr
        self.wgt = wgt

    def get_name(self):
        return self.name

    def get_ebc(self):
        return self.ebc

    def get_extr(self):
        return self.extr

    def get_wgt(self):
        return self.wgt

    def __str__(self):
        return self.name


class Hop:
    def __init__(self, name, alpha, wgt, time):
        self.name = name
        self.wgt = wgt
        self.alpha = alpha
        self.time = time

    def get_name(self):
        return self.name

    def get_wgt(self):
        return self.wgt

    def get_alpha(self):
        return self.alpha

    def get_time(self):
        return self.time

    def set_alpha(self, alpha):
        """ Compensate for stock with varying alpha levels."""
        self.alpha = alpha

    def __str__(self):
        return self.name