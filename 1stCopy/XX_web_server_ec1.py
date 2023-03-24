import socket
import sys
import os

HOST = 'localhost' # default host to listen on
PORT = 8080 # default port number to listen on

CRLF = '\r\n'

# get host and port numbers from command line arguments if provided
if len(sys.argv) > 1:
    HOST = sys.argv[1].split(':')[0]
    PORT = int(sys.argv[1].split(':')[1])

SP = ' '

def is_valid_http_request(request):
    """
    Validates the given HTTP request.
    Returns True if the request is valid, False otherwise.
    """
    try:
        # Split the request into its parts
        parts = request.split('\r\n\r\n')
        headers = parts[0].split('\r\n')
        body = parts[1] if len(parts) > 1 else None
    except:
        return False

    # Validate the request line
    if not headers[0].startswith('GET ') and not headers[0].startswith('POST '):
        return False

    # Validate the GET Request
    if headers[0].startswith('GET '):

        # Check that the "Host" header is present and has a value
        host_header = [line for line in headers  if line.startswith('Host: ')]
        if not host_header or len(host_header) > 1 or not host_header[0][6:]:
            return False
        
        # Check that the "User-Agent" header is present and has a value
        user_agent_header = [line for line in headers if line.startswith('User-Agent: ')]
        if not user_agent_header or len(user_agent_header) > 1 or not user_agent_header[0][12:]:
            return False
        
        # Check that the "Accept" header is present and has a value
        accept_header = [line for line in headers if line.startswith('Accept: ')]
        if not accept_header or len(accept_header) > 1 or not accept_header[0][8:]:
            return False
        
        # Check that the "Accept-Language" header is present and has a value
        accept_language_header = [line for line in headers if line.startswith('Accept-Language: ')]
        if not accept_language_header or len(accept_language_header) > 1 or not accept_language_header[0][17:]:
            return False
        
        # Check that the "Connection" header is present and has a value
        connection_header = [line for line in headers if line.startswith('Connection: ')]
        if not connection_header or len(connection_header) > 1 or not connection_header[0][12:]:
            return False
        
    # Validate the POST Request
    if headers[0].startswith('POST '):

        # Check that the "Host" header is present and has a value
        host_header = [line for line in headers  if line.startswith('Host: ')]
        if not host_header or len(host_header) > 1 or not host_header[0][6:]:
            return False
        
        # Check that the "User-Agent" header is present and has a value
        user_agent_header = [line for line in headers if line.startswith('User-Agent: ')]
        if not user_agent_header or len(user_agent_header) > 1 or not user_agent_header[0][12:]:
            return False
        
        # Check that the "Content-Type" header is present and has a value
        content_type_header = [line for line in headers if line.startswith('Content-Type: ')]
        if not content_type_header or len(content_type_header) > 1 or not content_type_header[0][14:]:
            return False
        
        # Check that the "Content-Length" header is present and has a value
        content_length_header = [line for line in headers if line.startswith('Content-Length: ')]
        if not content_length_header or len(content_length_header) > 1 or not content_length_header[0][16:]:
            return False
        
        #Check that the "Content-Length" header has a integral value
        for line in headers:
            if line.startswith('Content-Length: '):
                try:
                    int(line[16:])
                except:
                    return False

    # The request is valid
    return True

def handle_client(conn, addr):
    print(f'Client connected: {addr}')
    request_data = conn.recv(1024)
    response_data = generate_response(request_data)
    conn.sendall(response_data)
    conn.close()
    print(f'Client disconnected: {addr}')

def generate_response(request_data):
    request_str = request_data.decode()
    request_lines = request_str.split(CRLF)
    request_line_parts = request_lines[0].split(SP)

    # Returning bad request response if not a valid http request
    if not is_valid_http_request(request_str):
        print('valid request')
        return build_response(400, 'Bad Request')

    # Only support GET requests for now
    if request_line_parts[0] != 'GET':
        print('not get')
        return build_response(501, 'Not Implemented', {'Allow': 'GET'})

    path = request_line_parts[1]

    # Check if file exists in server directory
    file_path = os.path.join(os.getcwd(), path[1:])

    if os.path.exists(file_path):

        if file_path.endswith('index.html') or request_line_parts[1][1:] == '' :
            with open('index.html') as f:
                body = f.read()        
            header = {
                'Content-Type': 'text/html',
                'Content-Length': len(body)
            }
            return build_response(200, 'OK', header, body)
        
        else:
            with open('message.html') as f:
                body = f.read()
            header = {
                'Content-Type': 'text/html',
                'Content-Length': len(body)
            }
            return build_response(200, 'OK', header, body)
        
    else:
        return build_response(404, 'Not Found')  
      
def build_response(status_code, status_text, headers=None, body=None):
    response_lines = []
    response_lines.append(f'HTTP/1.1 {status_code} {status_text}')
    if headers:
        for header_name, header_value in headers.items():
            response_lines.append(f'{header_name}: {header_value}')
    if body:
        response_lines.append(CRLF+body)
    return (CRLF.join(response_lines)+CRLF).encode()

def start_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((host, port))
        server_sock.listen()

        print(f'Server listening on {host}:{port}')
        client_sock, client_addr = server_sock.accept()
        handle_client(client_sock, client_addr)

if __name__ == '__main__':
    start_server(HOST, PORT)
