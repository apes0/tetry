def getLocation(piece):
    # get the len of the longest part of a piece
    # 0 is there for pieces that are <2 layers
    l = max(0, *[len(layer) for layer in piece])
    # pieces start from x = 3, but an i piece would give x = 2
    return max(6 - l, 3)
