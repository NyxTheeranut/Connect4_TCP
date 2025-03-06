import socket
import threading
import time

class Connect4:
    def __init__(self):
        self.rows = 6
        self.cols = 7
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.current_player = 1
        self.lock = threading.Lock()
        self.winner = 0

    def drop_piece(self, col, player):
        with self.lock:
            if self.winner != 0 or self.current_player != player:
                return False
            if not (0 <= col < self.cols):
                return False
            for row in range(self.rows - 1, -1, -1):
                if self.board[row][col] == 0:
                    self.board[row][col] = player
                    return True
            return False

    def check_winner(self):
        with self.lock:
            for row in range(self.rows):
                for col in range(self.cols):
                    if self.board[row][col] != 0:
                        player = self.board[row][col]
                        if col + 3 < self.cols and all(self.board[row][col + i] == player for i in range(4)):
                            return player
                        if row + 3 < self.rows and all(self.board[row + i][col] == player for i in range(4)):
                            return player
                        if row + 3 < self.rows and col + 3 < self.cols and all(self.board[row + i][col + i] == player for i in range(4)):
                            return player
                        if row - 3 >= 0 and col + 3 < self.cols and all(self.board[row - i][col + i] == player for i in range(4)):
                            return player
            return 0

    def switch_player(self):
        with self.lock:
            if self.winner == 0:
                self.current_player = 3 - self.current_player

    def get_board_state(self):
        return self.board

host = "127.0.0.1"
port = 5555
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((host, port))
server_socket.listen(2)

print("Server started. Waiting for 2 players to connect...")
clients = []
game = Connect4()
game_ended = False  
lock = threading.Lock()

for i in range(2):
    client_socket, addr = server_socket.accept()
    clients.append(client_socket)
    print(f"Player {i + 1} connected from {addr}")
    client_socket.send(f"Player {i + 1}".encode())

def handle_client(client_socket, player_num):
    global game_ended
    opponent_socket = clients[1] if player_num == 1 else clients[0]
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if data:
                col = int(data.split()[-1])
                print(f"Player {player_num} attempts column {col}")
                if game.drop_piece(col, player_num):
                    game.winner = game.check_winner()
                    board_state = str(game.get_board_state())
                    if game.winner == 0:
                        game.switch_player()
                    msg = f"255|{board_state}|{game.current_player}|{game.winner}"
                    print(f"Sending to Player {player_num}: {msg}")
                    client_socket.send(msg.encode())
                    print(f"Sending to Player {3 - player_num}: {msg}")
                    opponent_socket.send(msg.encode())
                    if game.winner != 0:
                        with lock:
                            game_ended = True 
                        time.sleep(2)  
                        break
                else:
                    print(f"400|Player {player_num} move invalid: column {col}")
                    client_socket.send("400|Invalid move".encode())
        except Exception as e:
            print(f"Player {player_num} disconnected: {e}")
            break
    client_socket.close()
    opponent_socket.close()

thread1 = threading.Thread(target=handle_client, args=(clients[0], 1), daemon=True)
thread2 = threading.Thread(target=handle_client, args=(clients[1], 2), daemon=True)
thread1.start()
thread2.start()

try:
    while True:
        with lock:
            if game_ended:
                print("Game over detected, shutting down server...")
                time.sleep(1) 
                for client in clients:
                    client.close()
                server_socket.close()
                break
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Server shutting down manually...")
    for client in clients:
        client.close()
    server_socket.close()
