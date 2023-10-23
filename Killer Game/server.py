import socket
import pickle
from _thread import *

from game import Game
from network import Get, Reset

server = "localhost" # may need to replace
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    raise e

s.listen()
print("Waiting for a connection, Server Started")

games = dict() # {gameId: Game()}
idCount = 0
just_deleted_gameIds = []


def threaded_client(conn: socket.socket, player, gameId):
    global idCount
    conn.send(pickle.dumps(player))

    reply = ""
    while True:
        try: 
            data = pickle.loads(conn.recv(4096 * 2))

            if gameId in games:
                if data:
                    if isinstance(data, Reset):
                        games[gameId].reset()
                    elif not isinstance(data, Get) and isinstance(data, Game):
                        games[gameId] = data
                    
                    reply = games[gameId]
                    conn.sendall(pickle.dumps(reply))
                else:
                    break
            else:
                break
        except: 
            break
    
    if gameId not in just_deleted_gameIds:
        if not games[gameId].ready():
            games[gameId].unassign_role(player.playerno)
            if games[gameId].remove_game():
                games.pop(gameId, None)
        else:
            just_deleted_gameIds.append(gameId)
            games.pop(gameId, None)
    
    idCount -= 1
    conn.close()


while True:
    conn, addr = s.accept()
    print("---")
    print("Connected to :", addr)

    idCount += 1 # if idCount is 5, then p = 5, if idCount = 15, then p = 5

    if not just_deleted_gameIds:
        gameId = (idCount - 1) // 10 # starts from 0
    else:
        gameId = just_deleted_gameIds[0]
        just_deleted_gameIds.pop(0)

    if idCount % 10 == 1:
        games[gameId] = Game(gameId)
        print("Creating a new game...")
        print(games[gameId].roles)
    else:
        if gameId != max(games.keys()):
            gameId = max(games.keys())
    
    player = games[gameId].assign_role()

    start_new_thread(threaded_client, (conn, player, gameId))
