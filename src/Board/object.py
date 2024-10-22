class Object():
    def __init__(self, row, column, hitbox: tuple[int, int] | None = (1, 1)):
        self.row = row
        self.column = column
        self.hitbox = hitbox

    def is_piece(self):
        return type(self) == "Piece"
    
    def has_hitbox(self):
        return self.hitbox is not None
    
class Void(Object):
    def __init__(self, row, column):
        super().__init__(row, column)