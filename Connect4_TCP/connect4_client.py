import socket
import ast
import os
import threading
import time

# Clear terminal function (cross-platform)
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

# Display the board
def display_board(board):
    clear_terminal()
    print(" 0 1 2 3 4 5 6")
    for row in board:
        print("|" + " ".join(" " if cell == 0 else "X" if cell == 1 else "O" for cell in row) + "|")
    print("-" * 15)

# TCP Client Setup
host = "127.0.0.1"
port = 5555
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))
player_info = client_socket.recv(1024).decode()
player_num = int(player_info.split()[-1])
print(f"You are Player {player_num} (X for Player 1, O for Player 2)")

# Shared game state
board = [[0 for _ in range(7)] for _ in range(6)]
current_player = 1
winner = 0
lock = threading.Lock()
condition = threading.Condition(lock)  # For turn synchronization
turn_in_progress = False  # Track if a turn is being processed

# Receive updates from server
def receive_updates():
    global board, current_player, winner, turn_in_progress
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if data:
                with condition:
                    parts = data.split("|")
                    board = ast.literal_eval(parts[0])
                    current_player = int(parts[1])
                    winner = int(parts[2])
                    turn_in_progress = False  # Turn complete
                    print(f"Received update: {data}")
                    condition.notify_all()  # Notify waiting threads
        except Exception as e:
            print(f"Server disconnected: {e}")
            break

# Start receiving thread
receive_thread = threading.Thread(target=receive_updates, daemon=True)
receive_thread.start()

# Main loop for player input and display
while True:
    with lock:
        current_board = [row[:] for row in board]  # Deep copy of board
        current_turn = current_player
        game_winner = winner

    display_board(current_board)
    if game_winner != 0:
        print(f"Game Over! Player {game_winner} wins!")
        break

    with condition:
        if current_turn == player_num and not turn_in_progress:
            print("Your turn!")
            try:
                col = int(input("Enter column (0-6): "))
                if 0 <= col <= 6:
                    turn_in_progress = True
                    client_socket.send(str(col).encode())
                    # Wait for the server to switch turns
                    while current_player == player_num and turn_in_progress:
                        condition.wait(timeout=5)  # Wait until turn changes
                else:
                    print("Invalid column! Choose between 0 and 6.")
            except ValueError:
                print("Please enter a valid number.")
        else:
            print(f"Waiting for Player {current_turn}...")
            time.sleep(1)  # Refresh display and wait for updates

# Cleanup
print("Client shutting down...")
client_socket.close()
