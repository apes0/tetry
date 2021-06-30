import math


# park miller PRNG seeded with the seed of the seed
def parkMiller(seed):
    seed = seed % 0x7fffffff
    while True:
        seed = (16807*seed) % 0x7fffffff
        yield seed/0x7ffffffe


minos = ['z', 'l', 'o', 's', 'i', 'j', 't']


class Rng():
    def __init__(self, seed):
        self.rng = parkMiller(seed)

    def getBag(self):
        i = len(minos)
        bag = minos.copy()
        for i in range(i-1, 0, -1):
            j = math.floor(next(self.rng)*(i + 1))
            bag[i], bag[j] = bag[j], bag[i]
        return bag
