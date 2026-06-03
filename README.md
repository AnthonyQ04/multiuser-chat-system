# Multiuser Chat System

A TCP-based chat system built in Python and deployed on Ubuntu Server 24.04. This project involved building both a server and client from scratch, configuring a Linux VM, and designing a custom application layer protocol.

## What I Built
The server handles multiple client connections simultaneously and routes messages between users in real time. The client connects to the server, authenticates with a username and password, and allows users to send and receive messages. Everything runs on a Linux VM I configured myself, including SSH access and UFW firewall rules.

## Files
- `server.py` — manages client connections and message routing
- `client.py` — handles login and the messaging interface
- `protocol.txt` — defines the custom application layer protocol I designed
- `users.txt` — stores user credentials

## Technologies
Python, Ubuntu Server 24.04, TCP Sockets, UFW, SSH
