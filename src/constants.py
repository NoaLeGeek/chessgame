BROWN = (92, 64, 51)
WHITE = (255, 255, 255)

# Different values of pieces
piece_values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 100}

knight_directions = [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2)]
bishop_directions = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
rook_directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
queen_directions = bishop_directions + rook_directions
# -1 is O-O-O and 1 is O-O
castling_king_column = {-1: 2, 1: 6}
en_passant_direction = {2: 1, 5: -1}

sound_type = ["capture", "castle", "game-start", "game-end", "move-check", "move-opponent", "move-self", "premove", "promote"]
available_sound = ["beat", "default", "lolz", "marble", "metal", "nature", "newspaper", "silly", "space"]
available_board = ["blue", "brown", "green", "ic", "newspaper", "purple", "blue-marble", "blue2", "blue3", "canvas2", "green-plastic", "grey", "horsey", "leather", "maple", "maple2", "ncf-board", "olive", "pink-pyramid", "purple-diag", "wood", "wood2", "wood3", "wood4"]
available_background = ["standard", "game_room", "classic", "light", "wood", "glass", "tournament", "staunton", "newspaper", "tigers", "nature", "sky", "cosmos", "ocean", "metal", "gothic", "marble", "neon", "graffiti", "bubblegum", "lolz", "8_bit", "bases", "blues", "dash", "icy_sea", "walnut"]
available_piece = ['alpha', 'anarcandy', 'blindfold', 'caliente', 'california', 'cardinal', 'cburnett', 'celtic', 'chess7', 'chessnut', 'companion', 'disguised', 'dubrovny', 'fantasy', 'fresca', 'gioco', 'governor', 'horsey', 'icpieces', 'kiwen-suwi', 'kosal', 'leipzig', 'letter', 'libra', 'maestro', 'merida', 'mono', 'mpchess', 'pirouetti', 'pixel', 'reillycraig', 'riohacha', 'shapes', 'spatial', 'staunty', 'tatiana']