import socket        # need this to create network connections
import threading     # need this so multiple clients can connect at the same time
import logging       # this lets me save what happens on the server to a file

# setting up logging so I can track whats happening on the server
# it saves to server.log with the time and what happened
logging.basicConfig(
    filename="server.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

clients = {}         # I use this to keep track of who is connected right now
lock = threading.Lock()  # this prevents two threads from messing with clients at the same time

def load_users(filename):   # this function reads the username and passwords from a file
    users = {}              # start with empty dict then fill it in
    with open(filename, "r") as f:  # open the file
        for line in f:              # go through each line
            line = line.strip()     # remove extra spaces or newlines
            if ":" in line:         # make sure the line has a colon separating user and password
                username, password = line.split(":", 1)  # split into two parts
                users[username] = password               # store it
    return users  # give back the finished dictionary

users = load_users("users.txt")  # load all users when the server starts up

def broadcast(sender, msg):         # this sends a message to every connected user except the sender
    with lock:                      # lock before touching shared clients dict
        for username, conn in clients.items():  # loop through all connected users
            if username != sender:              # skip the person who sent it
                try:
                    conn.send(f"[{sender} -> everyone]: {msg}\n".encode())  # send broadcast message
                except:
                    pass  # if one client fails just move on to the next

def handle_client(conn, addr):    # this runs for each client that connects in its own thread
    logging.info(f"New connection from {addr}")  # log it so I can see whos connecting
    print(f"New connection from {addr}")         # also print it to the terminal
    conn.send("Enter username: ".encode())       # ask the client for their username
    username = conn.recv(1024).decode().strip()  # wait for them to send it back
    conn.send("Enter password: ".encode())       # now ask for their password
    password = conn.recv(1024).decode().strip()  # wait for the password
    if username not in users or users[username] != password:  # check if login is correct
        logging.warning(f"Failed login for {username} from {addr}")  # log the bad attempt
        conn.send("Authentication failed. Disconnecting.\n".encode())  # tell them it failed
        conn.close()  # kick them out
        return        # stop handling this client
    with lock:        # lock before touching the shared clients dict
        clients[username] = conn  # add them to the active clients list
    logging.info(f"{username} logged in from {addr}")  # log the successful login
    print(f"{username} logged in from {addr}")         # print it too
    conn.send(f"Welcome {username}! Type 'list' to see online users.\n".encode())  # send welcome
    while True:       # keep listening for messages from this client
        try:
            message = conn.recv(1024).decode().strip()  # wait for a message
            if not message:   # if nothing came in the client probably disconnected
                break         # exit the loop
            if message == "list":  # client wants to see whos online
                with lock:         # lock before reading clients
                    online = ", ".join(clients.keys())  # put all usernames in a string
                conn.send(f"Online users: {online}\n".encode())  # send the list back
                logging.info(f"{username} checked who is online")  # log it
            elif message.startswith("@all "):   # client wants to message everyone at once
                msg = message[5:]               # remove the @all part to get just the message
                broadcast(username, msg)        # send it to everyone else
                conn.send("Message sent to everyone.\n".encode())  # confirm to sender
                logging.info(f"{username} sent a broadcast message")  # log it
            elif message.startswith("@"):  # client is trying to message someone specific
                parts = message.split(" ", 1)   # split into the target and the message
                target = parts[0][1:]            # remove the @ to get just the username
                msg = parts[1] if len(parts) > 1 else ""  # get the actual message text
                with lock:                       # lock before looking up the target
                    target_conn = clients.get(target)  # find the targets connection
                if target_conn:                  # if they are online
                    target_conn.send(f"[{username}]: {msg}\n".encode())  # send them the message
                    conn.send(f"Message sent to {target}\n".encode())    # tell sender it worked
                    logging.info(f"{username} messaged {target}")        # log it
                else:
                    conn.send(f"User {target} is not online.\n".encode())  # tell sender they missed
                    logging.info(f"{username} tried to message offline user {target}")  # log it
            else:
                conn.send("Usage: @username message | @all message | list\n".encode())  # they typed something wrong
        except:
            break  # if anything breaks just exit the loop
    with lock:     # lock before removing them from the list
        clients.pop(username, None)  # remove disconnected user from active clients
    logging.info(f"{username} disconnected")  # log the disconnect
    print(f"{username} disconnected")         # print it too
    conn.close()   # close their connection

def main():               # this is where the server gets set up and started
    host = "0.0.0.0"      # listen on all interfaces so any device can connect
    port = 5000           # using port 5000 which I opened in the firewall with ufw
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a TCP socket
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # so I can restart without waiting
    server.bind((host, port))   # attach the socket to the port
    server.listen(5)            # start listening up to 5 connections waiting at once
    logging.info(f"Server started on port {port}")  # log server start
    print(f"Server started on port {port}")         # print it to terminal
    while True:                 # keep the server running forever
        conn, addr = server.accept()  # wait for someone to connect
        thread = threading.Thread(target=handle_client, args=(conn, addr))  # give them their own thread
        thread.daemon = True    # thread dies when main program dies
        thread.start()          # start handling that client

main()  # kick everything off
