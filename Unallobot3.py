#!/usr/bin/python
#Unallobot
# Uses Python 2.7.2

import socket
import ConfigParser
import time
import re

serverAddr = None
serverPort = None
serverChan = None
botNick = None
botPass = None
irc = None

def ping():			# Responding to Server Pings
	ircsock.send("PONG :Pong\n")


def send_msg(chan):
	ircsock.send("PRIVMSG "+ chan +" :" + msg + "\n")


def eightball(data):
	if data!='' and '?' in data:
			return choice(['It is certain.','It is decidedly so.','Without a doubt.','Yeirc. definitely.','You may rely on it.','As I see it, yeirc.','Most likely.','Outlook good.','Signs point to yeirc.','Yeirc.','Reply hazy, try again.','Ask again later.','Better not tell you now.','Cannot predict now.','Concentrate and ask again.','Don\'t count on it.','My reply is no.','My sources say no.','Outlook not so good.','Very doubtful.','Run Away!'])
	else:
		return 'I can do nothing unless you ask me a question....'


def address():
	return "512 Shaw Court #105, Severn, MD 21144"


def sign(data):		# Check the sign message or Change the sign Message
	return 'Not implemented yet.'


def status():		# Check the Status of the space
	return 'Not implemented yet.'


def bot_help(data):
	data = data.replace('.','')
	helps = {
				'status': '!status returns the current status of the space. (open/closed)',
				'sign': '!sign returns or updates the text displayed on the prolite LED sign.',
				'tweet': '!tweet returns the latest tweet on the @Unallocated twitter account.',
				'site': '!site returns the latest blog post on http://unallocatedspace.org/',
				'rollcall': '!rollcall lists Unallocated Space members that have checked into the space with their UAS member smart cards during the current session (opening to closing)',
				'weather': '!weather returns the weather conditions outside the space.',
				'address': address(),
				'wiki': '!wiki when used with text returns a link most closely related to the search term on the Unallocated Wiki.',
				'link': '!link returns various links to Unallocated Space related web pageirc. List can be altered here: http://www.unallocatedspace.org/wiki/Links',
				'video': '!video queries the Unallocated Space youtube account and returns the top result.',
	}
	if data in helps:
		return helps[data]
#	elif data in help_alias and help_alias[data] in helps:
#		ret = "!%s is an aliairc. "%data
#		return ret + helps[help_alias[data]]
	else:
		return 'Available commands are: !'+' !'.join(helpirc.keys())


def parse_conf(file):
	global serverAddr
	global serverPort
	global serverChan
	global botNick
	global botPass

	config = ConfigParser.ConfigParser()
	config.read(file)

	try:
		serverAddr = config.get('Server', 'server')
		serverPort = config.get('Server', 'port')
		serverChan = config.get('Server', 'channel')
		botNick = config.get('BotInfo', 'nickname')
		botPass = config.get('BotInfo', 'password')
	except ConfigParser.NoOptionError as e:
		print "Error parsing config file: " + e.message


def test_message():
	global serverAddr
	global serverPort
	global serverChan
	global botNick
	global botPass
	global irc

	botNick = "UnTeBot"

	irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print "connecting to: " + serverAddr + " " + serverPort
	irc.connect((serverAddr, int(serverPort)))
	irc.send('NICK %s\r\n' % (botNick,))
	irc.send('USER %s 8 * :%s\r\n' % (botNick, botNick))
	time.sleep(15)

	first = True
	while True:
		text = irc.recv(2048)

		print "received text: \"" + text + "\""

		if text.find("PING") != -1:
			temp = re.search("PING :[a-zA-Z0-9]+", text)
			if temp:
				pong = temp.group(0)
			else:
				pong = ""
			irc.send('PONG :' + pong[6:] + '\r\n')

			if first:
				time.sleep(2)
				print 'DEBUG: joining the channel'
				irc.send('JOIN %s\r\n' % (serverChan,))
				print 'DEBUG: joined'
				first = False

		if text.find("!test") != -1:
			test()


def test():
	irc.send("PRIVMSG %s :Test test test.\n" % (serverChan,))

parse_conf("Unallobot3.conf.temp")
test_message()

# add cli parsing for verbose (debug info), path to config (with default),
# optionally print info to stderr, always logfile, and detach as daemon (no stderr in that case)