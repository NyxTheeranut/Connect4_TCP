import socket
import ast
import os
import threading
import time

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_board(board, message=""):
    clear_terminal()
    print(" 0 1 2 3 4 5 6")
    for row in board:
        print("|" + " ".join(" " if cell == 0 else "X" if cell == 1 else "O" for cell in row) + "|")
    print("-" * 15)
    if message:
        print(message)

host = "127.0.0.1"
port = 5555
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))
player_info = client_socket.recv(1024).decode()
player_num = int(player_info.split()[-1])
print(f"You are Player {player_num} (X for Player 1, O for Player 2)")

board = [[0 for _ in range(7)] for _ in range(6)]
current_player = 1
winner = 0
lock = threading.Lock()
condition = threading.Condition(lock)
turn_in_progress = False

def receive_updates():
    global board, current_player, winner, turn_in_progress
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if data:
                with condition:
                    parts = data.split("|")
                    status = int(parts[0])
                    if status == 255:
                        board = ast.literal_eval(parts[1])
                        current_player = int(parts[2])
                        winner = int(parts[3])
                        display_board(board)
                        turn_in_progress = False
                        condition.notify_all()
                    elif status == 400:
                        display_board(board, "Invalid move! Try again.")
                        time.sleep(1)
                        turn_in_progress = False
                        condition.notify_all()
        except Exception as e:
            print(f"Server disconnected: {e}")
            break

receive_thread = threading.Thread(target=receive_updates, daemon=True)
receive_thread.start()

while True:
    with lock:
        current_board = [row[:] for row in board]
        current_turn = current_player
        game_winner = winner

    if game_winner != 0:
        display_board(current_board)
        print(f"Game Over! Player {game_winner} wins!")
        break

    with condition:
        if current_turn == player_num and not turn_in_progress:
            display_board(current_board)
            print("Your turn!")
            try:
                col = int(input("Enter column (0-6): "))
                turn_in_progress = True
                client_socket.send(f"Column {col}".encode())
                while turn_in_progress:
                    condition.wait(timeout=5)
            except ValueError:
                print("Please enter a valid number!")
                time.sleep(1)
        else:
            display_board(current_board)
            print(f"Waiting for Player {current_turn}...")
            time.sleep(1)

print("Client shutting down...")
client_socket.close()
