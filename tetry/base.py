class Base:
    def __init__(self, data, obj=None):
        for key, dat in data.items():
            if obj:
                dat = obj(dat)
            self.__dict__.update({key.strip('_'):dat})