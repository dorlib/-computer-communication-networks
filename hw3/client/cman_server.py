import socket
import argparse
from cman_game import Game, Player, MAX_ATTEMPTS, State
from cman_game_map import read_map
from cman_utils import *
import select

#  game object 
players = []
map_path="map.txt"
game_on = 0
cman_moved = 0
spirit_moved = 0
#player_can_move = {}
game = Game(map_path) 

player_roles= { 
    Player.SPIRIT: "spirit", 
    Player.CMAN: "Cman", 
    Player.OBSERVER: "observer"
}

def is_player(player_address):
    return player_address == game.players[Player.CMAN] or player_address == game.players[Player.SPIRIT] 

def join_game(sock, player_address, join_message):
    role = join_message["ROLE"]

    if not (Player.OBSERVER <= role <= Player.SPIRIT):
        print("Not a legal role")  # Send error message
        messages[name_to_opcode['error']]['DATA'][0] = b'\x01'
        sock.sendto(pack_message(name_to_opcode['error']), player_address)  # Send error message
        return False
    else:
        # Handle new player roles (synchronously)
        if role == Player.OBSERVER:  # Add new observer
            print(f"Welcome new observer {player_address}!")
            players.append(player_address)  # Add player to the list
            update_message = pack_message(name_to_opcode['update_state'])
            sock.sendto(update_message, player_address)  # Send game state
        else:
            if not game.players[role]:  # Check if CMAN or SPIRIT roles are free
                print(f"Welcome new {player_roles[role]} {player_address}!")
                players.append(player_address)  # Add player to the list
                update_message = pack_message(name_to_opcode['update_state'])
                sock.sendto(update_message, player_address)  # Send game state
                game.players[role] = player_address
                print(f"Sent the game state to {player_roles[role]}")

            else:
                print(f"{player_roles[role]} has already been taken :(")
                messages[name_to_opcode['error']]['DATA'][0] = b'\x02'
                print(messages[name_to_opcode['error']]['DATA'])
                
                sock.sendto(pack_message(name_to_opcode['error']), player_address)  # Send error message
                return False
            return True

def end_game(sock, player ):
    if game.winner == player:
        print(f"{player_roles[player]} won the game")
        messages[name_to_opcode["end"]]["WINNER"] = player
        messages[name_to_opcode["end"]]["S_SCORE"] = game.get_current_players_coords[Player.SPIRIT-1] # get coordinates of spirit
        messages[name_to_opcode["end"]]["C_SCORE"] = game.get_current_players_coords[Player.CMAN-1] # get coordinates of cman
                
        for client in players: # send the winning message to all
                sock.sendto(pack_message( messages[name_to_opcode["end"]]), client)
                
        # initialize parameters for the new game
        messages[name_to_opcode["end"]]["WINNER"] = b'\x00'
        messages[name_to_opcode["end"]]["S_SCORE"] = [b"\xFF", b"\xFF"] # get coordinates of spirit
        messages[name_to_opcode["end"]]["C_SCORE"] = [b"\xFF", b"\xFF"] # get coordinates of cman
        
        
        return True
    return False

def update_game(sock, player_address, can_move = 1):
    if not can_move: 
        messages[name_to_opcode["update_state"]]["FREEZE"] = 1
    
    messages[name_to_opcode["update_state"]]["C_COORDS"] = game.get_current_players_coords()[0]
    messages[name_to_opcode["update_state"]]["S_COORDS"] = game.get_current_players_coords()[1]
    messages[name_to_opcode["update_state"]]["ATTEMPTS"] = MAX_ATTEMPTS - game.lives 
    messages[name_to_opcode["update_state"]]["COLLECTED"] = game.get_points_byte_string()
    
    print(messages[name_to_opcode["update_state"]] )
    
    update_message = pack_message(name_to_opcode['update_state'])
    sock.sendto(pack_message(name_to_opcode['update_state']), player_address)
    
def move_player(sock, player_address, movement_message):
    global spirit_moved, cman_moved
    can_move = False
    if is_player(player_address):
        player = Player.CMAN if player_address[1] == game.players[Player.CMAN][1] else Player.SPIRIT
        direction = movement_message["DIRECTION"]
        can_move = game.apply_move(player, direction)  
        if player == Player.CMAN:
            cman_moved = 1
        if player == Player.SPIRIT:
            spirit_moved = 1
    else: # attempt to move an observer
        print(f"Observer can't move {player_address}!") 
        can_move = False
    return can_move
    
    
def quit_game(sock, player_address):
    # If the opcode is "quit", handle the quit message asynchronously
    global game_on
    print(f"Disconnected {player_address}")
    players.remove(player_address)  # Remove player from the list
    if game.players[Player.CMAN] == player_address:
        game.players[Player.CMAN] = 0
        if game_on:
           game.winner == Player.SPIRIT
           game.declare_winner(Player.CMAN)
           game_on = 0
    if game.players[Player.SPIRIT] == player_address:
        game.players[Player.SPIRIT] = 0
        if game_on:
           game.winner == Player.CMAN    
           game.declare_winner(Player.CMAN)
           game_on = 0
        
    return False
    
def play_game(sock, player_address):
    print ("started game!")
    global cman_moved, spirit_moved
    game.state = State.START
    no_error = True
    can_move = False
    while True: # game on loop 
        read_sockets, _, _ = select.select([sock], [], [],0.1)        
        for s in read_sockets:
            message, player_address = s.recvfrom(4096)  # Accept message from a player
            unpacked_message = unpack_message(message)    
            if unpacked_message["OPCODE"] == name_to_opcode["join"]:
                no_error = join_game(s, player_address, unpacked_message)
                    
            if unpacked_message["OPCODE"] == name_to_opcode["movement"]: # player movement command
                can_move = move_player(s, player_address, unpacked_message)        
                
            if unpacked_message["OPCODE"] == name_to_opcode["quit"]:
                no_error = quit_game(s, player_address) 
        if cman_moved or spirit_moved:
            cman_moved = 0
            spirit_moved = 0       
            for client in players:
                update_game(sock, client,can_move)
                
       
        
def wait_for_players(sock):
    global game_on
    players = []
    game_on = 0
    game.players[Player.CMAN] = 0
    game.players[Player.SPIRIT] = 0
    while True:
        # read_sockets, _, _ = select.select([sock], [], [])
        # sock = read_sockets[]
        message, player_address = sock.recvfrom(4096)  # Blocking call to accept other messages
        unpacked_message = unpack_message(message)
        opcode = unpacked_message["OPCODE"]
        
        if opcode == name_to_opcode['join']:
            join_game(sock, player_address, unpacked_message)

        if opcode == name_to_opcode['quit']:
            quit_game(sock, player_address)
            continue
        # Game-related actions (synchronous)
        if game.players[Player.CMAN] and game.players[Player.SPIRIT]:
            game_on = 1
            update_game( sock, game.players[Player.CMAN], 1)  # Send movement approval to CMAN
            update_game( sock, game.players[Player.SPIRIT], 1)  # Send movement approval to SPIRIT
            play_game(sock, player_address)  # Start the game
            
            
            
def main(port):
    # Create UDP socket
    ip = '0.0.0.0'#localhost'
    server_address = (ip, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #sock.setblocking(False)  # Set the socket to non-blocking mode
    sock.bind(server_address)  # Use appropriate IP and port
    print(f"Listening on {server_address}")
    wait_for_players(sock)

if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(description="Server - Cman game")
    parser.add_argument('-p', '--port', type=int, default=1337, help="Port to connect to (default: 1337)")
    args = parser.parse_args()
    main(args.port)
