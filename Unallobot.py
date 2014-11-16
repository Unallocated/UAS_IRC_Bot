#!/usr/bin/python
#Unallobot
# Uses Python 2.7.2

import pdb
import socket
import ConfigParser
import time
import re
import random
import threading
import json
import SocketServer
import os
import logging, logging.handlers
#import daemon

# todo: actually join the channel with the new channel method

class Bot:
    def __init__(self, conf_file):

        # set up logging services:
        self.logger = logging.getLogger('Bot')
        self.logger.setLevel(logging.DEBUG)
        FH = logging.handlers.RotatingFileHandler('/var/log/Bot.log','a',10000,20)
        FH.setLevel(logging.DEBUG)
        self.logger.addHandler(FH)
        self.logger.debug("starting")

        config = ConfigParser.ConfigParser()
        config.read(conf_file)

        try:
            self.serverAddr = config.get('Server', 'server')
            self.serverPort = config.get('Server', 'port')
            self.serverChan = config.get('Server', 'channel')
            self.botNick = config.get('BotInfo', 'nickname')[:9]
            self.botPass = config.get('BotInfo', 'password')
            self.OpperPW = config.get('OpperPW', 'password')
            #self.LogFile = config.get('Logging', 'logfile')
        except ConfigParser.NoOptionError as e:
            self.logger.error("Error parsing config file: " + e.message)

        # Irc connection
        self.irc = None

        # Need this to be the value from the temp_status file on the box
        self.LastStatus = None

        self.commands = {
            # 'test': self.test,
            'eightball': self.eightball,
            '8ball': self.eightball,
            'echo': self.echo,
            'address': self.address,
            'status': self.status,
            'help': self.helpme,
            'JSON': self.json_parser
        }

    def helpme(self,msg):
        keyslist=""
        self.irc.send(self.privmsg('Here is a list of valid commands: \n'))
        for keys in self.commands:
            if keys != 'JSON':
                keyslist = keyslist +'!' + keys + ', '
        self.irc.send(self.privmsg(keyslist))

    def privmsg(self, msg):
        return "PRIVMSG " + self.serverChan + " :" + msg + "\n"

    def test(self, msg):
        #print "In function test: %s" % self.privmsg('Test test test.')
        self.logger.debug("In function test %s" % self.privmsg('Test test test.'))
        self.irc.send(self.privmsg('Test test test.'))

    def echo(self, msg):
        self.irc.send(self.privmsg(msg))

    def join_channel(self):
        # TODO: Verify that the bot actually joined the channel.
        # if you try to join the channel immediately after pong, the server won't be ready yet.
        time.sleep(2)
        self.logger.debug("joining the channel %s" % self.serverChan) 
        self.irc.send('JOIN %s\r\n' % (self.serverChan,))
        self.logger.debug("joined %s" % self.serverChan)

    def ping(self, pong):            # Responding to Server Pings
        self.irc.send('PONG :' + pong + '\r\n')

    # this function is formatted like dog doo-doo - Crypt0s
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

    def sign(self, data):        # Check the sign message or Change the sign Message
        self.irc.send(self.privmsg('Not implemented yet.'))

    def status(self, data):        # Check the Status of the space
        #statusMsg = open('/tmp/status').read()[1:]
        #self.irc.send(self.privmsg( statusMsg))
        self.irc.send(self.privmsg(self.LastStatus))

    def json_parser(self,data):
        parsed_data = json.loads(data)
        self.irc.send(self.privmsg(parsed_data["Service"] + ' says ' + parsed_data["Data"]))
        if (parsed_data["Service"]=="Occupancy"):
            self.LastStatus = parsed_data["Service"] + ' says ' + parsed_data["Data"]    

    def connect_and_listen(self):
        self.joined_to_chan = False

        self.logger.debug("connecting to: " + self.serverAddr + " " + self.serverPort)

        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # if the bot recieves no socket traffic for 5 minutes, assume that it has been disconnected
        self.irc.settimeout(300)
        self.irc.connect((self.serverAddr, int(self.serverPort)))

        self.irc.send('NICK %s\r\n' % (self.botNick,))
        self.irc.send('USER %s 8 * :%s\r\n' % (self.botNick, self.botNick))

        # TODO: trigger the rest of this function on some output from the server MOTD.
        #time.sleep(15)


        while True:
            data = ''
            while data == '' or data[-1] != '\n':
                try:
                    data += self.irc.recv(1)
                except socket.timeout:
                    # couldn't read in 5 minutes -- assume heat death of universe has occured and retry
                    self.logger.debug('The bot TCP connection died a horrible death.  Ressurecting...')
                    self.irc.shutdown()
                    self.irc.close()
                    # this is recursive and bad.
                    self.connect_and_listen()
            if data == None:
                continue

            text = data
            self.logger.debug("recieved: \"" + data + "\"")
            tmp = text.split()[0]
            # Server Directive
            print tmp
            if tmp.upper()[1:] == self.serverAddr.upper():
                information = text.split(':')[1]
                if self.joined_to_chan == False and information.find("End of /MOTD command."):
                    self.join_channel()
                    self.joined_to_chan = True
            #ping
            elif tmp == "PING":
                pong = "PONG"
                if self.joined_to_chan == False:
                    temp = False
                    temp = re.search("PING :[a-zA-Z0-9]+", text)
                    if temp:
                        pong = temp.group(0)[6:]
                        self.join_channel()
                        self.joined_to_chan = True
                self.ping(pong)


            # We use continues when we know we no longer need to process anything
            elif tmp == "NOTICE":
                continue

            #user message
            else:
                user, cmd, destination = text.split()[:3]
                user = user.split('!')[0]
                message = text.split(':')[2:][0].strip()

                # TODO: May want to make this a case/switch associative array.
                if cmd == "JOIN":
                    continue

                if cmd == "KICK":
                    if message == self.botNick:
                        sleep(5)
                        self.join_channel()
                    else:
                        continue

                # if the message starts with a "!" then do something
                if message[:1] == "!":
                    user_cmd = message[1:].split()[0] #strip the !, then give me what's after it but before the next space
                    # If valid command, do eet
                    if user_cmd in self.commands.keys():
                        # TODO: In the future we will want to pass argument as an array and accept *args on all command functions
                        argument = message[len(user_cmd)+2:] # rest of the message string after the len of the command plus the !\  
                        self.commands[user_cmd](argument) # Run the function in self.commands that corresponds to the user_cmd
                        self.logger.debug("user " + user + ' issued command ' + user_cmd + " recieved with arg " + argument)

                    # invalid command - print help message
                    else:
                        self.commands['help']('')
                else:
                    continue

            #if cmd == "PRIVMSG":
'''
            text = data[1:]


            # TODO: autojoin on "End of /MOTD command"
            # TODO: Slice the text, don't use regex.
            if text.find("PING") == 0:
                # Handle the initial ping which prevents DDOS.
                # TODO: There should be a more robust way to join the channel.

            # Split the messages into parts, don't use regex
            elif text.find(self.serverChan + " :!") != -1:
                # take word right after '!' to the first whitespace, look up in dict of commands, where value is function
                try: 
                    command = text[text.find(' :!')+3:].split()[0]
                except:
                     self.commands['help']('')
                else: 
                    if (command in self.commands) and (command != "JSON"):
                        #print "Calling command %s" % (command,)
                        self.logger.debug("Calling command %s" % (command,))
                        self.commands[command](text[text.find(' :!') + 4 + len(command):])
                    else: self.commands['help'](command)
            elif text.find(self.botNick + " :!JSON") != -1: #Direct Message JSON request
                try:
                    self.commands['JSON'](text[text.find(' :!') + 8:])
                except IOError:
                    self.irc.send(self.privmsg("Stop Attacking the bot"))
            elif (text.find(self.botNick + " :!Op") != -1): #Direct Message Request to Op Someone in IRC
                TempPW = (text[text.find(' :!') + 6:text.find(' :!') + 14])
                UserToBeOppd = text[text.find(' :!')+15:]
                TestOut = "MODE " + self.serverChan + " +o " + UserToBeOppd
                if (TempPW == self.OpperPW):
                    self.irc.send("MODE " + self.serverChan + " +o " + UserToBeOppd)
                    self.logger.info("Opping %s" % UserToBeOppd) 
'''

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        DataToPost = self.data[self.data.find(' :!') + 7:]
        bot.json_parser(DataToPost)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    HOST = ''
    PORT_A = 9999

    TA = open('/opt/uas/UAS_IRC_Bot/Bot.pid','w')
    pid=str(os.getpid())
    TA.write(pid)
    TA.close()

    #thread for the external listener
    print "started the API listening service"
    server_A = ThreadedTCPServer((HOST, PORT_A),ThreadedTCPRequestHandler)
    server_A_thread = threading.Thread(target=server_A.serve_forever)
    server_A_thread.setDaemon(True)
    server_A_thread.start()
        
    #instantiate the bot -- wrapped in a try/except in case we can't get to the config file.
    print "doing the bot"
    try:
        bot = Bot("/opt/uas/UAS_IRC_Bot/Unallobot.conf")
    except:
        print "We couldn't start the bot.  Check your configuration file?  should be /opt/uas/UAS_IRC_Bot/Unallobot.conf"
        exit(1)

    print "Starting the thread for the bot"
    # The IRC Part is run in a separate thread
    server_B_thread = threading.Thread(target=bot.connect_and_listen)
    server_B_thread.setDaemon(True)
    server_B_thread.start()

    while True:
        # TODO: Handle signals here
        pass

    # we need to clean up the pid file so that the run script in init will be in the proper state    
    #os.remove('/opt/uas/UAS_IRC_Bot/Bot.pid')
