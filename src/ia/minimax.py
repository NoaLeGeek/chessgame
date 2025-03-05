from enigma.machine import EnigmaMachine

def enigma(machine, secret_message, key, rotor_start):
    machine.set_display(rotor_start)
    msg_key = machine.process_text(key)
    machine.set_display(msg_key)
    decrypted_message = machine.process_text(secret_message)
    return decrypted_message

message = "Garry Kasparov est un joueur dechecs sovietique puis russe Il est le treizieme champion du monde dechecs de lhistoire Cependant il aurait avoue que VSCode est meilleur que VSCodium"
machine = EnigmaMachine.from_key_sheet(
    rotors='I II V',
    reflector='B',
    ring_settings='11 10 02',
    plugboard_settings='ZJ BP VK UG LN QX SA MT ED YH')
print(enigma(machine, message, "VSC", "SAV"))

class Minimax():
    def __init__(self, depth: int):
        self.depth = depth

    def get_best_move(self):
        pass