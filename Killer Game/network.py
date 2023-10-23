import socket
import pickle

from game import Game
from roles import Player


class Reset:
    pass


class Get:
    pass


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "localhost" # may need to replace
        self.port = 5555 
        self.addr = (self.server, self.port)
        self.player = self.connect()

    def get_player(self):
        return self.player

    def connect(self) -> Player:
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048)) #player
        except:
            pass

    def send(self, data: Game | Get | Reset) -> Game:
        self.client.send(pickle.dumps(data))
        
        return pickle.loads(self.client.recv(2048 * 6)) # Game()
