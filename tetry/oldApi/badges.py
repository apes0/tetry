from .base import Base
import dateutil.parser

def getBadges(data):
    out = []
    for badge in data:
        out.append(Badge(badge))
    return out

class Badge(Base):
    def __init__(self, data):
        self.ts = None
        super().__init__(data)
        if 'ts' in self.__dict__.keys():
            if self.ts:
                self.obtainedat = dateutil.parser.parse(self.ts)