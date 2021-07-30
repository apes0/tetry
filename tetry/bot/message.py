import struct

import msgpack

# packer


def standartId(data):
    prefix = b'\x45'
    return prefix + msgpack.packb(data)  # just prefix + msgpack blob


def batchTag(data):
    msg = b'\x58'
    msgs = []  # all messages
    for m in data:
        packed = pack(m)  # pack each message by itself
        # add the len of the new message to the full message
        msg += struct.pack('!I', len(packed))
        msgs.append(packed)
    msg += b'\x00\x00\x00\x00'  # seperation for messages and lens
    for m in msgs:
        msg += m  # add all messages to the message
    return msg


def extensionTag(data):
    prefix = b'\xB0'
    return prefix + data  # just prefix + binary data


def extractedId(data, id):
    prefix = b'\xAE'
    id = struct.pack('!I', id)
    return prefix + id + msgpack.packb(data)


# pack data

def pack(data):
    if isinstance(data, bytes):  # only extension tags are a bytes object
        d = extensionTag(data)
    elif isinstance(data, list):  # only batch tags are a dict object, which is missing an id member
        d = batchTag(data)
    elif isinstance(data, tuple):
        d = extractedId(data[1], data[0])
    elif 'id' in data:
        # extracted id tags are also a dict, but have an id member
        d = extractedId(data, data['id'])
    else:
        d = standartId(data)  # only standart id tags are binary blobs
    return d


# unpacker

def unpackBatchTag(data):
    lens = []
    for i in range(0, len(data), 4):  # get all lens
        n = data[i:i+4]
        n = struct.unpack('!I', n)[0]
        if not n:  # if len is 0 stop
            break
        lens.append(n)
    start = (len(lens) + 1)*4  # get the start of the data in the messages
    data = data[start:]
    out = []
    for l in lens:  # unpack every message
        res = unpack(data[:l])
        out.append(res)
        data = data[l:]
    return out


def unpackExtractedId(data):
    id = data[:4]
    res = msgpack.unpackb(data[4:])
    id = struct.unpack('!I', id)[0]
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
