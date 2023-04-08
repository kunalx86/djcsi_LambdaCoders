import socket

# host and port to listen on
HOST = 'localhost'
PORT = 8080

# create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to a public host and a port
sock.bind((HOST, PORT))

# listen for incoming connections
sock.listen(5)

while True:
    # accept connections
    conn, addr = sock.accept()
    print(f'Connection from {addr[0]}:{addr[1]}')

    # receive data from the connection
    data = conn.recv(1024)

    # log the packet information
    print(f'Source IP: {addr[0]}, Source port: {addr[1]}, Destination IP: {HOST}, Destination port: {PORT}')
    print(f'Packet data: {data}')

    # forward the packet to its original destination
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(data)

    # close the connection
    conn.close()
