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

def extractedId(data):
    prefix = b'\xAE'
    id = data['id']
    id = struct.pack('!I', id)
    return prefix + id + msgpack.packb(data)


# pack data

def pack(data, ws):
    if isinstance(data, bytes): # only extension tags are a bytes object
        d = extensionTag(data)
    elif isinstance(data, list): # # only batch tags are a dict object
        d = batchTag(data)
    elif 'id' in data:
        d = extractedId(data)
        ws.bot.messageId += 1
    else:
        d = standartId(data)
    return d


# unpacker

def unpackBatchTag(data):
    lens = []
    for i in range(0, len(data), 4):
        n = data[i:i+4]
        n = struct.unpack('!I', n)[0]
        if not n:
            break
        lens.append(n)
    start = (len(lens) + 1)*4
    data = data[start:]
    out = []
    for l in lens:
        res = unpack(data[:l])
        out.append(res)
        data = data[l:]
    return out

def unpackExtractedId(data):
    id = data[:4]
    res = msgpack.unpackb(data[4:])
    return (id, res)


# unpack data

def unpack(data):
    prefix = data[0]
    d = data[1:]
    if prefix == 0x45:
        d = msgpack.unpackb(d)
    elif prefix == 0x58:
        d = unpackBatchTag(d)
    elif prefix == 0xAE:
        d = unpackExtractedId(d)
    return d