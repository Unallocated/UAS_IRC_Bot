#!/usr/bin/python
#Unallobot
# Uses Python 2.7.2

import socket
import ConfigParser

serverAddr = None
serverPort = None
serverChan = None
botNick = None
botPass = None

def ping():			# Responding to Server Pings
	ircsock.send("PONG :Pong\n")


def send_msg(chan):
	ircsock.send("PRIVMSG "+ chan +" :" + msg + "\n")


def eightball(data):
	if data!='' and '?' in data:
			return choice(['It is certain.','It is decidedly so.','Without a doubt.','Yes. definitely.','You may rely on it.','As I see it, yes.','Most likely.','Outlook good.','Signs point to yes.','Yes.','Reply hazy, try again.','Ask again later.','Better not tell you now.','Cannot predict now.','Concentrate and ask again.','Don\'t count on it.','My reply is no.','My sources say no.','Outlook not so good.','Very doubtful.','Run Away!']) 
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
				'link': '!link returns various links to Unallocated Space related web pages. List can be altered here: http://www.unallocatedspace.org/wiki/Links',
				'video': '!video queries the Unallocated Space youtube account and returns the top result.',
	}
	if data in helps:
		return helps[data]
#	elif data in help_alias and help_alias[data] in helps:
#		ret = "!%s is an alias. "%data
#		return ret + helps[help_alias[data]]
	else:
		return 'Available commands are: !'+' !'.join(helps.keys())


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

	print "serverAddr: " + serverAddr
	print "serverPort: " + serverPort
	print "serverChan: " + serverChan
	print "botNick: " + botNick
	print "botPass: " + botPass

parse_conf('Unallobot3.conf.temp')