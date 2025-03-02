# Connect 4 Multiplayer Game

This project is a multiplayer Connect 4 game that uses a TCP server for communication between players and a Streamlit-based frontend for interaction.

## Features
- Multiplayer gameplay with two players.
- A server-client architecture using Python's `socket` module.
- Real-time game updates.
- Streamlit-based UI for interactive play.
- Improved game logic for handling edge cases.
- Automatic game restart after a match ends.

## Requirements
Ensure you have the following installed:
- Python 3.x
- Streamlit (`pip install streamlit`)

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/connect4.git
   cd connect4
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Running the Server
Start the game server to handle player connections:
```sh
python server.py
```

## Running the Streamlit Client
Each player should run the client separately:
```sh
streamlit run client.py
```

## How It Works
1. The server (`connect4_server.py`) waits for two players to connect.
2. Each player runs 2 of either of the client (`connect4_client.py`,`connect4_client_streamlit.py`), which connects to the server.
3. Players take turns dropping pieces into the grid.
4. The game board updates in real time.
5. The game announces the winner when a player gets four pieces in a row.
6. The game automatically resets after a winner is declared or a draw occurs.

## Game Rules
- Players take turns dropping pieces into a 7-column, 6-row board.
- The first player to connect four pieces in a row (horizontally, vertically, or diagonally) wins.
- If the board is full with no winner, the game ends in a draw.

