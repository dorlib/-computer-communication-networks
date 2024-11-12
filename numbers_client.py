import socket

def tcp_client():
    # Define server address and port
    server_address = '127.0.0.1'  # localhost
    server_port = 1337

    # Create a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # Connect to the server
        client_socket.connect((server_address, server_port))
        print("Connected to the server")

        user = "User:" +input("User:")
        password = "Password:"+input("Password:")

        # Send data to the server
        message = user
        client_socket.sendall(message.encode())
        print(f"Sent: {message}")

        # Receive data from the server
        response = client_socket.recv(1024)
        print(f"Received: {response.decode()}")

        # Send data to the server
        message = password
        client_socket.sendall(message.encode())
        print(f"Sent: {message}")

        # Receive data from the server
        response = client_socket.recv(1024)
        print(f"Received: {response.decode()}")

        while True:
            # Send data to the server
            command = input("enter command: ")
            client_socket.send(command.encode())
            if command == "quit":
                break
            # Receive data from the server
            response = client_socket.recv(1024)
            print(f"Received: {response.decode()}")
        client_socket.close()
# Run the client
tcp_client()
