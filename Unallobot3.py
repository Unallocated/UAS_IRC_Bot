#!/usr/bin/python
#Unallobot
# Uses Python 2.7.2

import socket

def ping(): # Responding to Server Pings
	ircsock.send("PONG :Pong\n")

def sendmsg (chan):
	ircsock.send("PRIVMSG "+ chan +" :" + msg + "\n")

