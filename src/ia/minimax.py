from enigma.machine import EnigmaMachine

# Set up the Enigma machine
machine = EnigmaMachine.from_key_sheet(
   rotors='IV I V',
   reflector='B',
   ring_settings='20 5 10',
   plugboard_settings='SX KU QP VN JG TC LA WM OB ZF')
# Set the initial position of the Enigma rotors
machine.set_display('FNZ')
# Encrypt the text 'BFR' and store it as msg_key
msg_key = machine.process_text('BFR')
print(msg_key)
plaintext = "RASPERRYPI"
ciphertext = machine.process_text(plaintext)
print(ciphertext)

class Minimax():
    def __init__(self, depth: int):
        self.depth = depth

    def get_best_move(self):
        pass