import msgpack
import struct


# packer

def standartId(data):
    prefix = b'\x45'
    return prefix + msgpack.packb(data)

def batchTag(data):
    prefix = b'\x58'
    # struckt pack with !I
    return prefix + msgpack.packb(data)

def extensionTag(data):
    prefix = b'\xB0'
    return prefix + data


# pack data

def pack(data):
    if isinstance(data, bytes): # only extension tags are a bytes object
        d = extensionTag(data)
    elif isinstance(data, list): # # only batch tags are a dict object
        d = batchTag(data)
    else:
        d = standartId(data)
    return d


# unpacker

def unpackBatchTag(data):
    dat = data.split(b'\x00\x00\x00\x00')
    lens = []
    for i in range(len(dat[0])//4):
        n = dat[0][i:i+4]
        n = struct.unpack('!I', n)
        lens.append(n)

# unpack data

def unpack(data):
    pass