import requests
import dateutil
from .endcontext import Endcontext
from .urls import recordUrl
from .base import Base

class Records(Base):
    def __init__(self, data):
        self.zen = Record(data['zen'])
        records = data['records']
        super().__init__(records, Record)
        self.fourtyLines = self.__dict__['40l'] # items starting with intingers do not work

class Record(Base):
    def __init__(self, data):
        super().__init__(data)
        if 'record' in self.__dict__:
            record = self.record
            if not record:
                return None
            self.stream = record['stream']
            self.id = record['replayid']
            self.time = dateutil.parser.parse(record['ts'])
            self.endcontext = Endcontext(record['endcontext'])

def getRecords(name):
    url = recordUrl(name.lower())
    with requests.Session() as ses:
        resp = ses.get(url).json()
        if not resp['success']:
            raise Exception(resp['error'])
    json = resp['data']
    return Records(json)