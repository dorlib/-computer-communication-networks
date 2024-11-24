#!/usr/bin/python3

import socket
import sys

DEFAULT_PORT = 1337
DEFAULT_HOST = "localhost"
autneticated = False


def validate_auth_creds(cred, field):
    parts = cred.split(":")
    if len(parts) == 2:  # Ensure there's exactly one colon
        key, value = parts[0].strip().lower(), parts[1].strip()
        if key == field:
            return value
        else:
            return None
    else:
        return None

def parse_arguments():
    """
    Parses and validates command-line arguments for hostname and port.
    :return: A tuple of (hostname, port)
    """
    if len(sys.argv) == 1:
        # No arguments: use defaults
        return DEFAULT_HOST, DEFAULT_PORT
    elif len(sys.argv) == 2:
        # Only hostname is provided: use default port
        if sys.argv[1].isdigit():
            print("Error: Cannot provide a port without a hostname.")
            return None
        return sys.argv[1], DEFAULT_PORT
    elif len(sys.argv) == 3:
        # Both hostname and port are provided: validate port
        try:
            port = int(sys.argv[2])
            return sys.argv[1], port
        except ValueError:
            print("Error: Port must be an integer.")
            return None
    else:
        print("Usage: numbers_client.py [hostname [port]]")
        return None

def tcp_client():
    """Creates a TCP client"""
    # Retrieve and validate hostname and port
    result = parse_arguments()
    if result is None:
        return  # Exit gracefully
    server_address, server_port = result
    # Create a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # Connect to the server
        client_socket.connect((server_address, server_port))

        print("Welcome! Please log in")

        # Login loop
        while True:
            # Prompt the user for username and password
            username = input("")
            name = validate_auth_creds(username, "user")
            if name == None:
                break
            
            password = input("")
            password = validate_auth_creds(password, "password")
            if password == None:
                break

            credentials = f"{name}:{password}\n"
            client_socket.send(credentials.encode())

            # Receive the authentication result from the server
            response = client_socket.recv(1024).decode()
            print (response)  # Print the response from the server

            # If the login is unsuccessful, prompt for retry
            if "Failed to login" in response:
                continue
            else:
                autneticated = True
                break  # Authentication successful, exit loop

        # After successful login, move to command loop
        while True:
            if not autneticated:
                break
            command = input()
            client_socket.send(command.encode())
            if command.lower() == "quit":
                break
            # Receive and print the server's response
            response = client_socket.recv(1024)
            if response == b"error: unrecognized command" or response == b"error: invalid command format":
                break
            print(response.decode())


# Run the client
if __name__ == "__main__":
    tcp_client()
