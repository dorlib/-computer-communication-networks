import socket
import argparse
from cman_game import Player, Direction, Game
from cman_utils import *
from cman_game_map import *
import os
import sys
map_path="map.txt"
move_keys = {'w', 'a', 's', 'd'}
player_roles= { 
    Player.SPIRIT: "spirit", 
    Player.CMAN: "Cman", 
    Player.OBSERVER: "observer"

}
game = Game(map_path)
board_width = game.board_dims[0]
board_height = game.board_dims[1]
quit_condition = 'q' in get_pressed_keys()
prev_cman_coords = [0,0]
prev_spirit_coords = [0,0]
key_to_direction = {
    'w': Direction.UP,
    's': Direction.DOWN,
    'a': Direction.LEFT, 
    'd': Direction.RIGHT
}

def set_points_from_byte_string(byte_string):
    """
    Converts a byte string representation of points back into a dictionary
    of (i, j) -> value pairs where 1 represents a point and 0 represents no point.

    Args:
        byte_string (bytes): The byte string representing the points.
    """
    # Convert the byte string into a bit string
    bit_string = bin(int.from_bytes(byte_string, byteorder='big'))[2:].zfill(board_width * board_height)
    
    # Rebuild the points dictionary
    points = {
        (i, j): 1 if bit_string[i * board_height + j] == '1' else 0
        for i in range(board_width)
        for j in range(game.board_dims[1])
    }
    return points


        
def display_game(update_message):
        # Clear the screen before displaying the updated game state
        clear_print()
        print(f"Attempts: {update_message["ATTEMPTS"]}")
        points = set_points_from_byte_string(update_message["COLLECTED"])

        num_points = 40- sum(value == 1 for value in points.values())
        print(f"Collected: {num_points} points")
        new_cman_coords = update_message["C_COORDS"]
        new_spirit_coords = update_message["S_COORDS"]
        update_map (prev_cman_coords, prev_spirit_coords, new_cman_coords, new_spirit_coords, map_path)
        print_map(map_path)
        prev_cman_coords = new_cman_coords
        prev_spirit_coords = new_spirit_coords
        
def move_player(sock, server_address):
    pressed_move_keys = move_keys.intersection(get_pressed_keys() )
    if pressed_move_keys: # one of the keys has been pressed
        key = pressed_move_keys[0]
        messages[name_to_opcode["movement"]] = key_to_direction[key]
        sock.sendto(pack_message(messages[name_to_opcode["movement"]]), server_address)
      
def update_game(sock, server_address):
        update_message,server =sock.recvfrom(4096)
        unpacked_update_message= unpack_message(update_message)
        if unpacked_update_message["OPCODE"] == name_to_opcode["update"]:
            display_game(unpacked_update_message)
        if unpacked_update_message["OPCODE"] == name_to_opcode["end"]:
            print(f"winner is {player_roles[unpacked_update_message["WINNER"]]}!")

def start_game(sock, server_address):
    points = game.points # initial value of points
    while not quit_condition: # keep playing until quiting 
        move_player(sock, server_address)
        update_game(sock, server_address)
    quit(sock, server_address)
    
def quit(sock, server_address):
    quit_message = pack_message(messages[name_to_opcode['quit']]) # quit from server
    sock.sendto(quit_message, server_address)
    print("quitted")
    # Close the socket
    sock.close()
    
def main(role, addr, port):
    # Define server address and port
    server_address = (addr, port)
    # Send the chosen role to the server (you can use it for your message content)
    # Create UDP socket
    print("Welcome to the game!")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  
    # Send message to server
    messages[name_to_opcode['join']]['ROLE'] = role 
    join_message = pack_message(name_to_opcode['join'])
    sock.sendto(join_message, server_address)
    
    # Receive response from server
    update_message,server = sock.recvfrom(4096)
    unpacked_update_message = unpack_message(update_message) 
    
    print(f"Received game state: {unpacked_update_message}")
    
    print("waiting for game to start...")
    if role == 0: # observer
        start_game(sock)
        
    while not quit_condition:  
        
        movement_message,server =sock.recvfrom(4096)
        unpacked_movement_message= unpack_message(movement_message)
        if unpacked_movement_message["OPCODE"] == name_to_opcode["update"]:
            print("client has started playing")
            prev_cman_coords = unpacked_movement_message["C_COORDS"]
            prev_spirit_coords = unpacked_movement_message["S_COORDS"]
            start_game(sock)
        
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
