import math

class HopIBU:
    def __init__(self):
        """Calculator to derive brew IBU. The basic formula is:
        IBU = W * A * U / V * 10
        where
        W = Weight in grams
        A = Alpha %
        U = Utilisation %
        V = Wort volume in litres

        The Tinseth method* uses the following formula for
        boil gravity correction:
        F = 1.5673 * (0.000125 ** (SG - 1))

        and the following for utilisation:
        U = 25.367715 (1 - e ** (-0.04 * t)
        where t = boil time in minutes

        n.b. actual vol being boiled = 38 l, so multiply
        OG by 60 / 38 = 1.56 boil gravity - seems to work OK
        in the boil gravity correction factor, though Tinseth
        gives 1.65 as an empirical factor

        * https://realbeer.com/hops/research.html"""

    def get_tinseth_IBU(self):
        # boil gravity correction factor:
        f = 1.56 * (0.000125 ** (1.035 - 1))
        print('f ', f)
        # utilisation:
        u = 25.367715 * (1 - math.e ** (-0.04 * 90)) * f
        # calculate IBU:
        IBU = 20 * 18.7 * u / 600
        print('IBU = ', IBU)


hopIBU = HopIBU()
hopIBU.get_tinseth_IBU()
