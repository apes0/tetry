from .base import Base

class Endcontext(Base):
    def __init__(self, data):
        super().__init__(data)
        self.clears = Clears(self.clears)
        self.finesse = Finesse(self.finesse)
        del self.garbage
        self.time = self.finalTime

class Clears(Base):
    def __init__(self, data):
        super().__init__(data)

class Finesse(Base):
    def __init__(self, data):
        super().__init__(data)