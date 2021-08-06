class Board:
    def __init__(self):
        self.board = [[0]*10]*40
 
    def collides(self, piece, x, y):  # check if a piece collides with the board
        for _y in range(len(piece)):
            layer = piece[_y]
            for _x in range(len(layer)):
                piece = layer[_x]
                print(_y + y, _x + x, piece)
                if piece and self.board[_y + y][_x + x]:
                    return True
        return False
 

