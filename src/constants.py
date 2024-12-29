BROWN = (92, 64, 51)
WHITE = (255, 255, 255)

# The different gamemodes available in the game
gamemodes = ["Classic", "KOTH", "+3 Checks", "Giveaway", "Chess960"]

knight_directions = [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2)]
bishop_directions = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
rook_directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
queen_directions = bishop_directions + rook_directions
# 1 is O-O-O and -1 is O-O
castling_king_column = {1: 6, -1: 2}
en_passant_row = {2: 1, 5: -1}

ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "0": 0}
rowsToRanks = {v: k for k, v in ranksToRows.items()}
fileToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
colsToFiles = {v: k for k, v in fileToCols.items()}