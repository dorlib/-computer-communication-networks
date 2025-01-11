import socket
import argparse
from cman_game import Player, Direction, Game
from cman_utils import *
from cman_game_map import *
import os
import sys
import select 

map_path="map.txt"
game = Game(map_path)
points = game.points # initial value of points
attempts =0 
lives = 0
num_points = 0
board_width = game.board_dims[0]
board_height = game.board_dims[1]
prev_cman_coords = [-1,-1]
prev_spirit_coords = [-1,-1]
move_keys = ['w', 'a', 's', 'd']
quit_key = ['q']
rows= None
overwritten_spot = 'F'

player_roles= { 
    Player.SPIRIT: "spirit", 
    Player.CMAN: "Cman", 
    Player.OBSERVER: "observer"

}


key_to_direction = {
    'w': Direction.UP,
    's': Direction.DOWN,
    'a': Direction.LEFT, 
    'd': Direction.RIGHT
}

def quit_condition():
    global quit_key
    return 'q' in get_pressed_keys(quit_key)
def set_points(bytes_list):
    """
    Converts a byte list representation of points back into a dictionary
    of (i, j) -> value pairs where 1 represents a point and 0 represents no point.
    """
    global board_width, board_height, points
    value = 0
    print(bytes_list)
    bit_list = [] 
    for i, byte in enumerate(bytes_list):
        
        if (byte ==0):
            bit_list.extend([0,0,0,0,0,0,0,0])
        else: 
            binary_value = [int(bit) for bit in list(bin(byte)[2:].zfill(8))]
            bit_list.extend(binary_value)            
    print(bit_list)
    # Convert the byte string into a bit string
    #print("bit_list", bit_list)
    points_list =  sorted(points.keys(), key=lambda x: (x[0], x[1]))
    #print("point_list", points_list)
    # Rebuild the points dictionary
    points = {point: bit for point, bit in zip(points_list, bit_list)}
    #print("points", points)
    return points
def display_winner(update_message):
    
        print("\033[H\033[J", end="")
        print(update_message)
        
        winner = player_roles[update_message["WINNER"]]
        print(f"winner is {winner}!")
        num_points = update_message["C_SCORE"]
        num_catch = update_message["S_SCORE"]
        print(f"Cman Collected: {num_points} points")
        print(f"Spirit catched Cman: {num_points} times")
        

def display_game(update_message):
        # Clear the screen before displaying the updated game state
        print("\033[H\033[J", end="")
        print(update_message)
        global num_points, attempts, lives, overwritten_spot
        global prev_cman_coords, prev_spirit_coords,rows  # Declare as global
        attempts = update_message["ATTEMPTS"]
        points = set_points(update_message["COLLECTED"])
        num_points = sum(value == 1 for value in points.values())
        
        new_cman_coords = update_message["C_COORDS"]
        new_spirit_coords = update_message["S_COORDS"]

        #update_map (prev_cman_coords, prev_spirit_coords, new_cman_coords, new_spirit_coords,points,  map_path)
        
        rows, overwritten_spot = update_map(prev_cman_coords, prev_spirit_coords, new_cman_coords, new_spirit_coords, points, rows, file_path="map.txt",
                          collected_points=num_points, attempts=attempts, lives =lives, overwritten_spot = overwritten_spot)
        
        prev_cman_coords = new_cman_coords
        prev_spirit_coords = new_spirit_coords
        
def move_player(sock, server_address):
    global move_keys

    pressed_move_keys = get_pressed_keys(move_keys) 
    if pressed_move_keys: # one of the keys has been pressed
        key = pressed_move_keys[0]
        messages[name_to_opcode["movement"]]["DIRECTION"] = key_to_direction[key]
        sock.sendto(pack_message(name_to_opcode["movement"]), server_address)
      
def update_game(sock, server_address):
    read_sockets, _, _ = select.select([sock], [], [],0.1)
    for s in read_sockets:
        update_message,server =sock.recvfrom(4096)
    
    unpacked_update_message= unpack_message(update_message)
    
    if unpacked_update_message["OPCODE"] == name_to_opcode["update_state"]:
        display_game(unpacked_update_message)
    if unpacked_update_message["OPCODE"] == name_to_opcode["end"]:
        
        display_winner(unpacked_update_message)
        
        time.sleep(10)
        quit(sock, server_address)
        

def start_game(sock, server_address):
    print("\033[H\033[J", end="")
    while True: # keep playing until quiting 
        
        if quit_condition():
            quit(sock, server_address)
        move_player(sock, server_address)
        read_sockets, _, _ = select.select([sock], [], [],0.1)
        for s in read_sockets:
            update_game(sock, server_address)
    
def quit(sock, server_address):
    quit_message = pack_message(name_to_opcode['quit']) # quit from server
    sock.sendto(quit_message, server_address)
    print("quitted")
    # Close the socket
    sock.close()
    clear_map()
    exit(0)
    
def main(role, addr, port):
    # Define server address and port
    server_address = (addr, port)
    # Send the chosen role to the server (you can use it for your message content)
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  
    # Send message to server
    messages[name_to_opcode['join']]['ROLE'] = role 
    join_message = pack_message(name_to_opcode['join'])
    sock.sendto(join_message, server_address)
    load_map()
            # Receive response from server
    update_message,server = sock.recvfrom(4096)
    unpacked_message = unpack_message(update_message) 
    print(f"Received game state: {unpacked_message}")
    
    if role == Player.OBSERVER: # observer
        print(f"Welcome new {player_roles[role]}!")
        print("waiting for game to start...")
        start_game(sock, server_address)
    
    if unpacked_message["OPCODE"] == name_to_opcode["error"]: # in case of an error
        print("received error, quitting")
        print (unpacked_message["DATA"] )
        sock.close()
        clear_map()
        exit(1)
    
    print(f"Welcome new {player_roles[role]}!")
    print("waiting for game to start...")
    
 
    while True:  
        read_sockets, _, _ = select.select([sock], [], [],0.1)
        for s in read_sockets:
            update_game(s, server_address)
            start_game(sock, server_address)
        if quit_condition():
            quit(sock, server_address)
    
    
# Entry point for the script
if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Client for the game")
    parser.add_argument('role', type=int, help="Role the player wants to choose")
    parser.add_argument('addr', type=str, help="Server address (e.g., localhost or IP address)")
    parser.add_argument('-p', '--port', type=int, default=1337, help="Server port (default: 12345)")
    # Parse arguments
    args = parser.parse_args()
    # Call the main function with parsed arguments
    main(args.role, args.addr, args.port)
