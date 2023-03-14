import socket

def handle_request(client_socket):
    request_data = client_socket.recv(1024) # Receive request data from client
    request_lines = request_data.decode().split("\r\n")
    request_method, request_path, request_protocol = request_lines[0].split()

    # Prepare response data
    if request_path == "/":
        response_body = "Hello, World!"
    else:
        response_body = "404 Not Found"

    response_headers = [
        "Content-Type: text/html",
        f"Content-Length: {len(response_body)}",
        "Connection: close"
    ]

    # Send response data to client
    response = "\r\n".join([
        f"{request_protocol} 200 OK",
        *response_headers,
        "",
        response_body
    ])
    client_socket.sendall(response.encode())

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 8080))
    server_socket.listen()

    print("Listening on http://localhost:8080")

    while True:
        client_socket, address = server_socket.accept()
        print(f"Accepted connection from {address}")
        handle_request(client_socket)
        client_socket.close()

if __name__ == "__main__":
    main()
