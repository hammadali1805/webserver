import socket
import sys
import os
import re

HOST = 'localhost' # default host
PORT = 8000 # default port number 

# get host and port numbers from user
if len(sys.argv) > 1:
    try:
        HOST = sys.argv[1].split(':')[0]
        PORT = int(sys.argv[1].split(':')[1])
    except:
        print("Please provide a proper socket.")

def validate_http_rqst(rqst):
    # Define regular expression patterns for different parts of the HTTP request
    http_method_pattern = r"(GET|HEAD|POST|PUT|DELETE|CONNECT|OPTIONS|TRACE)"
    uri_pattern = r"(/[^\s]*)"
    http_version_pattern = r"(HTTP\/[0-9]\.[0-9])"
    header_pattern = r"([\w-]+):\s*([^\r\n]*)"
    
    # Validate the HTTP request using regular expressions
    match = re.match(f"{http_method_pattern}\s+{uri_pattern}\s+{http_version_pattern}\r\n", rqst.decode())
    if not match:
        return False
    
    headers = re.findall(header_pattern, rqst.decode())
    if not headers:
        return False
    
    for header in headers:
        if not re.match(header_pattern, f"{header[0]}: {header[1]}"):
            return False
    
    return True

def user_status(connection, address):
    print(f'User connected: {address}')
    rqst_data = connection.recv(1024)
    rpns_data = generate_rpns(rqst_data)
    connection.sendall(rpns_data)
    connection.close()
    print(f'User disconnected: {address}')

def generate_rpns(rqst_data):
    rqst_parts = rqst_data.decode().split('\r\n')[0].split(' ')

    # Build bad request response if not a valid http request
    if not validate_http_rqst(rqst_data):
        return build_rpns(400, 'Bad Request')

    # Build not implemented response if not a GET request
    elif rqst_parts[0] != 'GET':
        return build_rpns(501, 'Not Implemented', {'Allow': 'GET'})

    # Check if file exists
    file_location = os.path.join(os.getcwd(), rqst_parts[1][1:].replace('/', '\\'))
    
    if os.path.exists(file_location):

        if file_location.endswith('index.html') or rqst_parts[1][1:] == '' :
            with open('index.html') as f:
                body = f.read()        
            header = {
                'Content-Type': 'text/html',
                'Content-Length': len(body)
            }
            return build_rpns(200, 'OK', header, body)
        
        else:
            with open('message.html') as f:
                body = f.read()
            header = {
                'Content-Type': 'text/html',
                'Content-Length': len(body)
            }
            return build_rpns(200, 'OK', header, body)
        
    else:
        return build_rpns(404, 'Not Found')
    
def build_rpns(status_code, status_text, headers=None, body=None):
    rpns_lines = []
    rpns_lines.append(f'HTTP/1.1 {status_code} {status_text}')
    if headers:
        for header_name, header_value in headers.items():
            rpns_lines.append(f'{header_name}: {header_value}')
    if body:
        rpns_lines.append('\r\n'+body)
    return ('\r\n'.join(rpns_lines)+'\r\n').encode()

def start_web_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen()

        print(f'Server started listening on {host}:{port}')
        user_sock, user_addr = sock.accept()
        user_status(user_sock, user_addr)

if __name__ == '__main__':
    start_web_server(HOST, PORT)
