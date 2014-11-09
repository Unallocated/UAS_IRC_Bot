#!/usr/bin/python
#Unallobot
# Uses Python 2.7.2

import socket
import ConfigParser
import time
import re
import random


class Bot:
	def __init__(self, conf_file):
		self.serverAddr = None
		self.serverPort = None
		self.serverChan = None
		self.botNick = None
		self.botPass = None
		self.irc = None
		self.conf_file = conf_file
		self.first = True

		self.commands = {
			'test': self.test,
			'eightball': self.eightball,
			'8ball': self.eightball,
			'echo': self.echo,
			'address': self.address,
			'status': self.status,
			'help': self.helpme
		}

		self.parse_conf(self.conf_file)

#	def bot_help(self, data):
#		data = data.replace('.','')
#		helps = {
#					'status': '!status returns the current status of the space. (open/closed)',
#					'sign': '!sign returns or updates the text displayed on the prolite LED sign.',
#					'tweet': '!tweet returns the latest tweet on the @Unallocated twitter account.',
#					'site': '!site returns the latest blog post on http://unallocatedspace.org/',
#					'rollcall': '!rollcall lists Unallocated Space members that have checked into the space with their UAS member smart cards during the current session (opening to closing)',
#					'weather': '!weather returns the weather conditions outside the space.',
#					'address': self.address,
#					'wiki': '!wiki when used with text returns a link most closely related to the search term on the Unallocated Wiki.',
#					'link': '!link returns various links to Unallocated Space related web pageirc. List can be altered here: http://www.unallocatedspace.org/wiki/Links',
#					'video': '!video queries the Unallocated Space youtube account and returns the top result.',
#		}
#		if data in helps:
#			return helps[data]
	#	elif data in help_alias and help_alias[data] in helps:
	#		ret = "!%s is an aliairc. "%data
	#		return ret + helps[help_alias[data]]
#		else:
#			return 'Available commands are: !'+' !'.join(helpirc.keys())

	def parse_conf(self, file):
		config = ConfigParser.ConfigParser()
		config.read(file)

		try:
			self.serverAddr = config.get('Server', 'server')
			self.serverPort = config.get('Server', 'port')
			self.serverChan = config.get('Server', 'channel')
			self.botNick = config.get('BotInfo', 'nickname')
			self.botPass = config.get('BotInfo', 'password')
		except ConfigParser.NoOptionError as e:
			print "Error parsing config file: " + e.message

	def helpme(self,msg):
		#if 'msg'= #list of commands
		self.irc.send(self.privmsg('Here is a list of valid commands: \n'))
		for keys in self.commands:
			self.irc.send(self.privmsg(' !' + keys))

	def privmsg(self, msg):
		return "PRIVMSG " + self.serverChan + " :" + msg + "\n"

	def test(self, msg):
		print "In function test: %s" % self.privmsg('Test test test.')
		self.irc.send(self.privmsg('Test test test.'))

	def echo(self, msg):
		self.irc.send(self.privmsg(msg))

	def ping(self, pong):			# Responding to Server Pings
		self.irc.send('PONG :' + pong + '\r\n')
		if self.first:
			time.sleep(2)
			print 'DEBUG: joining the channel'
			self.irc.send('JOIN %s\r\n' % (self.serverChan,))
			print 'DEBUG: joined'
			self.first = False

	def eightball(self, data):
		if data != '' and '?' in data:
				self.irc.send(self.privmsg(random.choice(['It is certain.',
														  'It is decidedly so.',
														  'Without a doubt.',
														  'Yeirc. definitely.',
														  'You may rely on it.',
														  'As I see it, yeirc.',
														  'Most likely.',
														  'Outlook good.',
														  'Signs point to yeirc.',
														  'Yeirc.',
														  'Reply hazy, try again.',
														  'Ask again later.',
														  'Better not tell you now.',
														  'Cannot predict now.',
														  'Concentrate and ask again.',
														  'Don\'t count on it.',
														  'My reply is no.',
														  'My sources say no.',
														  'Outlook not so good.',
														  'Very doubtful.',
														  'Run Away!'])))
		else:
			self.irc.send(self.privmsg('I can do nothing unless you ask me a question....'))

	def address(self, data):
		self.irc.send(self.privmsg("512 Shaw Court #105, Severn, MD 21144"))

	def sign(self, data):		# Check the sign message or Change the sign Message
		self.irc.send(self.privmsg('Not implemented yet.'))

	def status(self, data):		# Check the Status of the space
		statusMsg = open('/tmp/status').read()[1:]
		self.irc.send(self.privmsg( statusMsg))
		#self.irc.send(self.privmsg('Not implemented yet.'))

	def connect_and_listen(self):
		self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print "connecting to: " + self.serverAddr + " " + self.serverPort
		self.irc.connect((self.serverAddr, int(self.serverPort)))
		self.irc.send('NICK %s\r\n' % (self.botNick,))
		self.irc.send('USER %s 8 * :%s\r\n' % (self.botNick, self.botNick))
		time.sleep(15)

		while True:
			data = 'a'
			while data[-1] != '\n':
				data += self.irc.recv(1)

			text = data[1:]

			print "received text: \"" + text + "\""

			if text.find("PING") == 0:
				temp = re.search("PING :[a-zA-Z0-9]+", text)
				if temp:
					pong = temp.group(0)[6:]
				else:
					pong = "pong"
				self.ping(pong)

			elif text.find(self.serverChan + " :!") != -1:
				# take word right after '!' to the first whitespace, look up in dict of commands, where value is function
				command = text[text.find(' :!')+3:].split()[0]
				if command in self.commands:
					print "Calling command %s" % (command,)
					self.commands[command](text[text.find(' :!') + 4 + len(command):])


bot = Bot("Unallobot3.conf.temp")
bot.connect_and_listen()

# add cli parsing for verbose (debug info), path to config (with default),
# optionally print info to stderr, always logfile, and detach as daemon (no stderr in that case)
