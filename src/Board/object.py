class Object():
    def __init__(self, row, column):
        self.row = row
        self.column = column

    def is_piece(self):
        return type(self) == "Piece"
    
class Void(Object):
    def __init__(self, row, column):
        super().__init__(row, column)