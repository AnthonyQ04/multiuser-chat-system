import socket    # need this to connect to the server over the network
import threading # need this so I can receive messages while also waiting for input
import sys       # need this in case I need to exit cleanly

def receive_messages(sock):      # this runs in the background and listens for incoming messages
    while True:                  # keep listening until something breaks
        try:
            message = sock.recv(1024).decode()  # wait for a message from the server
            if message:                          # make sure its not empty
                print(message, end="", flush=True)  # print it right away without waiting
        except:
            break  # if the connection drops just stop

def main():
    host = "127.0.0.1"  # the server is running on the same machine so I use localhost
    port = 5000          # has to match the port the server is listening on

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a TCP socket
    sock.connect((host, port))  # connect to the chat server

    prompt = sock.recv(1024).decode()      # server sends the username prompt first
    print(prompt, end="", flush=True)      # show it to the user
    username = input()                      # get the username they type
    sock.send(username.encode())           # send it to the server

    prompt = sock.recv(1024).decode()      # server sends the password prompt next
    print(prompt, end="", flush=True)      # show it to the user
    password = input()                      # get the password they type
    sock.send(password.encode())           # send it to the server

    response = sock.recv(1024).decode()    # server responds with welcome or failure
    print(response, end="", flush=True)    # show the response to the user

    if "failed" in response:  # if login failed no point continuing
        sock.close()           # close the connection
        return                 # exit the program

    thread = threading.Thread(target=receive_messages, args=(sock,))  # start background listener
    thread.daemon = True   # this thread dies when the main program exits
    thread.start()         # start it up

    while True:            # now just wait for the user to type messages
        try:
            message = input()          # get whatever they type
            if message:                # make sure its not blank
                sock.send(message.encode())  # send it to the server
        except:
            break  # if anything goes wrong just exit

    sock.close()  # close the socket when done

main()  # start the client
