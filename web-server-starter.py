#!/usr/bin/env python3

import argparse

import sys
import itertools
import socket
from socket import socket as Socket

# A simple web server


def main():

    # Command line arguments. Use a port > 1024 by default so that we can run
    # without sudo, for use as a real server you need to use port 80.
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', default=2080, type=int,
                        help='Port to use')
    args = parser.parse_args()

    # Create the server socket (to handle tcp requests using ipv4), make sure
    # it is always closed by using with statement.
    with Socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        # The socket stays connected even after this script ends. So in order
        # to allow the immediate reuse of the socket (so that we can kill and
        # re-run the server while debugging) we set the following option. This
        # is potentially dangerous in real code: in rare cases you may get junk
        # data arriving at the socket.
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server_socket.bind(('', args.port))
        server_socket.listen(1)

        print("server ready")

        while True:

            with server_socket.accept()[0] as connection_socket:
                # This is a hackish way to make sure that we can receive and process multi
                # line requests.
                request=""
                received=connection_socket.recv(1024).decode('utf-8')
                request+=received
                reply = http_handle(request)
                connection_socket.sendall(reply.encode('utf-8'))

            print("\n\nReceived request")
            print("======================")
            print(request.rstrip())
            print("======================")


            print("\n\nReplied with")
            print("======================")
            print(reply.rstrip())
            print("======================")


    return 0


def http_handle(request_string):
    """Given a http requst return a response

    Both request and response are unicode strings with platform standard
    line endings.
    """
    
    data = 'HTTP/1.1 200 OK\r\n'
    data+= 'Connection: keep-alive\r\n'
    data+= 'Content-Type: text/html; encoding=utf-8\r\n'
    f = open('index.html', 'r')
    # send data per line
    for l in f.readlines():
        data+=l
    f.close()
    data+="\r\n\r\n"


    if "favicon" in request_string:
        data="HTTP/1.1 404 Not Found\r\n\r\n"

    return data
    #assert not isinstance(request_string, bytes)


    # Fill in the code to handle the http request here. You will probably want
    # to write additional functions to parse the http request into a nicer data
    # structure (e.g., not a string) and to easily create http responses.

    # Used Figure 2.8 in book as guideline: Request line and Header lines
    # Step 0: Split the string by line
    # Step 1: Get the first line (request line) and split into method, url, version
    # Step 2: Until you see <CR><LF> (\r\n), read lines as key, value with header name and value. Store as a dictionary
    # Step 3: Check to make sure method, url, and version are all compliant
        # Step 3a: if method is a GET and url is "/" or "/index.html" and correct HTTP version, we need to respond with 200 OK and some HTML
        # Step 3b: If method is compliant, but not implemented, we need to respond with a correct HTTP response 
        # Step 3c: If the version is not compliant, we need to respond with correct HTTP response
        # Step 3d: If file does not exist in server path, respond with HTTP 404 File not found response
    # Step 4: Checking to make sure headers are correctly formatted

    raise NotImplementedError

    pass



if __name__ == "__main__":
    sys.exit(main())
