import json

file_path = 'data/encoded_moves.json'

rows = list(range(1, 9)) 
columns = ["a", "b", "c", "d", "e", "f", "g", "h"]  
squares = [f"{c}{r}" for c in columns for r in rows]

moves = [f"{s1}{s2}" for s1 in squares for s2 in squares if s1 != s2]

pieces = ["q", "r", "b", "n"]  
for piece in pieces:
    for h in ((7, 8), (2, 1)):  
        for i in range(1, 7):  
            moves.append(f"{columns[i]}{h[0]}{columns[i-1]}{h[1]}{piece}")
            moves.append(f"{columns[i]}{h[0]}{columns[i+1]}{h[1]}{piece}")
            moves.append(f"{columns[i]}{h[0]}{columns[i]}{h[1]}{piece}")
        moves.append(f"{columns[0]}{h[0]}{columns[0]}{h[1]}{piece}")
        moves.append(f"{columns[0]}{h[0]}{columns[1]}{h[1]}{piece}")
        moves.append(f"{columns[7]}{h[0]}{columns[7]}{h[1]}{piece}")
        moves.append(f"{columns[7]}{h[0]}{columns[6]}{h[1]}{piece}")


encoded_moves = {move: i for i, move in enumerate(moves)}
    
with open(file_path, "w") as file:
    json.dump(encoded_moves, file)
