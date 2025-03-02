# import socket
# import ast
# import os
# import threading
# import time

# # Clear terminal function (cross-platform)
# def clear_terminal():
#     os.system('cls' if os.name == 'nt' else 'clear')

# # Display the board
# def display_board(board):
#     clear_terminal()
#     print(" 0 1 2 3 4 5 6")
#     for row in board:
#         print("|" + " ".join(" " if cell == 0 else "X" if cell == 1 else "O" for cell in row) + "|")
#     print("-" * 15)

# # TCP Client Setup
# host = "127.0.0.1"
# port = 5555
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client_socket.connect((host, port))
# player_info = client_socket.recv(1024).decode()
# player_num = int(player_info.split()[-1])
# print(f"You are Player {player_num} (X for Player 1, O for Player 2)")

# # Shared game state
# board = [[0 for _ in range(7)] for _ in range(6)]
# current_player = 1
# winner = 0
# lock = threading.Lock()
# condition = threading.Condition(lock)  # For turn synchronization
# turn_in_progress = False  # Track if a turn is being processed

# # Receive updates from server
# def receive_updates():
#     global board, current_player, winner, turn_in_progress
#     while True:
#         try:
#             data = client_socket.recv(1024).decode()
#             if data:
#                 with condition:
#                     parts = data.split("|")
#                     board = ast.literal_eval(parts[0])
#                     current_player = int(parts[1])
#                     winner = int(parts[2])
#                     turn_in_progress = False  # Turn complete
#                     print(f"Received update: {data}")
#                     condition.notify_all()  # Notify waiting threads
#         except Exception as e:
#             print(f"Server disconnected: {e}")
#             break

# # Start receiving thread
# receive_thread = threading.Thread(target=receive_updates, daemon=True)
# receive_thread.start()

# # Main loop for player input and display
# while True:
#     with lock:
#         current_board = [row[:] for row in board]  # Deep copy of board
#         current_turn = current_player
#         game_winner = winner

#     display_board(current_board)
#     if game_winner != 0:
#         print(f"Game Over! Player {game_winner} wins!")
#         break

#     with condition:
#         if current_turn == player_num and not turn_in_progress:
#             print("Your turn!")
#             try:
#                 col = int(input("Enter column (0-6): "))
#                 if 0 <= col <= 6:
#                     turn_in_progress = True
#                     client_socket.send(str(col).encode())
#                     # Wait for the server to switch turns
#                     while current_player == player_num and turn_in_progress:
#                         condition.wait(timeout=5)  # Wait until turn changes
#                 else:
#                     print("Invalid column! Choose between 0 and 6.")
#             except ValueError:
#                 print("Please enter a valid number.")
#         else:
#             print(f"Waiting for Player {current_turn}...")
#             time.sleep(1)  # Refresh display and wait for updates

# # Cleanup
# print("Client shutting down...")
# client_socket.close()

import streamlit as st
import socket
import ast
import time

# Custom CSS for styling
st.markdown("""
    <style>
    .board-container {
        background-color: #1e3a8a;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .cell {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 60px;
        height: 60px;
        background-color: white;
        border-radius: 50%;
        margin: 5px;
        font-size: 40px;
    }
    .player-turn {
        font-size: 24px;
        font-weight: bold;
        margin: 10px 0;
    }
    .red-player {
        color: #ef4444;
    }
    .yellow-player {
        color: #facc15;
    }
    .winner {
        font-size: 28px;
        font-weight: bold;
        color: #10b981;
        text-align: center;
        margin-top: 20px;
    }
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #2563eb;
    }
    </style>
""", unsafe_allow_html=True)

# TCP Client Setup
def setup_client():
    if 'socket' not in st.session_state:
        host = "127.0.0.1"
        port = 5555
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(1.0)  # Non-blocking with timeout
        client_socket.connect((host, port))
        player_info = client_socket.recv(1024).decode()
        st.session_state.socket = client_socket
        st.session_state.player_num = int(player_info.split()[-1])
        st.session_state.board = [[0 for _ in range(7)] for _ in range(6)]
        st.session_state.current_player = 1
        st.session_state.winner = 0
        st.session_state.connected = True
    return st.session_state.player_num

# Display the board
def display_board():
    st.write(f"### Connect 4 - Player {st.session_state.player_num}", key="title")
    with st.container():
        st.markdown('<div class="board-container">', unsafe_allow_html=True)
        for row in st.session_state.board:
            cols = st.columns(7)
            for col_idx, cell in enumerate(row):
                with cols[col_idx]:
                    if cell == 0:
                        st.markdown('<div class="cell">⚪</div>', unsafe_allow_html=True)
                    elif cell == 1:
                        st.markdown('<div class="cell">🔴</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="cell">🟡</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Poll for server updates
def poll_server():
    try:
        data = st.session_state.socket.recv(1024).decode()
        if data:
            parts = data.split("|")
            st.session_state.board = ast.literal_eval(parts[0])
            st.session_state.current_player = int(parts[1])
            st.session_state.winner = int(parts[2])
    except socket.timeout:
        pass  # Timeout is expected; just continue polling
    except Exception as e:
        st.session_state.connected = False
        st.error(f"Connection error: {e}")

# Main Streamlit app
def main():
    st.title("Connect 4 - Multiplayer Edition")
    player_num = setup_client()

    if not st.session_state.connected:
        st.error("Failed to connect to server. Please restart the server and try again.")
        return

    # Poll server for updates
    poll_server()

    # Player indicator
    if st.session_state.current_player == 1:
        st.markdown('<p class="player-turn red-player">Player 1\'s Turn (Red)</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="player-turn yellow-player">Player 2\'s Turn (Yellow)</p>', unsafe_allow_html=True)

    # Display the board
    display_board()

    # Player input
    if st.session_state.winner == 0:
        if st.session_state.current_player == player_num:
            col_choice = st.selectbox(
                f"Choose a column (0-6)",
                range(7),
                key=f"select_{player_num}"
            )
            if st.button("Drop Piece", key=f"button_{player_num}"):
                st.session_state.socket.send(str(col_choice).encode())
                time.sleep(0.1)  # Small delay for server response
                poll_server()
                st.rerun()
        else:
            st.write(f"Waiting for Player {st.session_state.current_player}...")
            time.sleep(1)
            st.rerun()
    else:
        st.markdown(f'<p class="winner">Player {st.session_state.winner} Wins!</p>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()