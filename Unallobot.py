#!/usr/bin/env python
#Unallobot
# Uses Python 2.7.2 or Python 3
BUFFER_SIZE = 512

from argparse import ArgumentParser
from json import loads
from logging import DEBUG, INFO, ERROR, basicConfig, debug, info, error, getLogger, handlers
from os import getpid
from random import choice
from re import search
from socket import AF_INET, SOCK_STREAM, socket, timeout
from sys import exit
from threading import Thread
from time import sleep
from select import select

import signal,pdb

try:  # Python 3
	from configparser import ConfigParser, NoOptionError
	from socketserver import BaseRequestHandler, ThreadingMixIn, TCPServer
except ImportError as e:
	from ConfigParser import ConfigParser, NoOptionError
	from SocketServer import BaseRequestHandler, ThreadingMixIn, TCPServer
# todo: actually join the channel with the new channel method

class Bot:
    def __init__(self, conf_file, loglevel, logfilename):

        # set up logging services:
        self.logger = getLogger('Bot')
        self.logger.setLevel(loglevel)
        FH = handlers.RotatingFileHandler(logfilename,'a',10000,20)
        FH.setLevel(DEBUG)
        self.logger.addHandler(FH)
        self.logger.debug("starting")

        config = ConfigParser()
        config.read(conf_file)

        try:
            self.serverAddr = config.get('Server', 'server')
            self.serverPort = config.get('Server', 'port')
            self.serverChan = config.get('Server', 'channel')
            self.botNick = config.get('BotInfo', 'nickname')[:9]
            self.botPass = config.get('BotInfo', 'password')
            self.OpperPW = config.get('OpperPW', 'password')
            self.checkin_file = config.get('Checkin','checkin_file')
            #TODO: Check that all of these settings are legit before just taking them at face value
            #self.LogFile = config.get('Logging', 'logfile')
        except NoOptionError as e:
            self.logger.error("Error parsing config file: " + e.message)

        # Irc connection
        self.irc = None

        # Need this to be the value from the temp_status file on the box
        self.LastStatus = "/tmp/status"

        self.commands = {
            # 'test': self.test,
            'eightball': self.eightball,
            '8ball': self.eightball,
            'echo': self.echo,
            'address': self.address,
            'status': self.status,
            'help': self.helpme,
            'test':self.test,
            'checkin':self.checkin,
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
        try:
            retstr = "PRIVMSG " + self.serverChan + " :" + msg + "\n"
        except:
            retstr = "error occured"
        return retstr

    def test(self, msg):
        #debug("In function test: %s" % self.privmsg('Test test test.'))
        self.logger.debug("In function test %s" % self.privmsg('Test test test.'))
        self.irc.send(self.privmsg('Test test test.'))

    def echo(self, msg):
        self.irc.send(self.privmsg(msg))

    def checkin(self,msg):
        with open(self.checkin_file,'r') as checkin:
            users = ''.join(checkin.readlines())
        msg = "The following users have checked in: " + users
        self.irc.send(self.privmsg(msg))

    def join_channel(self):
        # TODO: Verify that the bot actually joined the channel.
        # if you try to join the channel immediately after pong, the server won't be ready yet.
        sleep(2)
        self.logger.debug("Joining the channel %s" % self.serverChan) 
        self.irc.send(("JOIN %s\r\n" % self.serverChan).encode("UTF-8"))
        response = self.get_next_line()
        if "You have not registered" in response:
            raise Exception("Unable to join channel: %s" % response)
        self.logger.debug("Joined %s" % self.serverChan)

    def ping(self, pong):            # Responding to Server Pings
        self.irc.send(("PONG : %s\r\n" % pong).encode("UTF-8"))

    # this function is formatted like dog doo-doo - Crypt0s
    def eightball(self, data):
        if data != '' and '?' in data:
                self.irc.send(self.privmsg(choice(['It is certain.',
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
        try:
            with open('/tmp/status') as statusfile:
                statusMsg = statusfile.readlines()
            statusMsg = ''.join(statusMsg).strip()
        except:
            statusMsg = "An error occured when attempting to read the status"
        self.irc.send(self.privmsg(statusMsg))            
        #self.irc.send(self.privmsg(self.LastStatus))

    def json_parser(self,data):
        parsed_data = loads(data)
        self.irc.send(self.privmsg(parsed_data["Service"] + ' says ' + parsed_data["Data"]))
        if (parsed_data["Service"]=="Occupancy"):
            self.LastStatus = parsed_data["Service"] + ' says ' + parsed_data["Data"]    

    def get_next_line(self,timeout=300):
        """
        This will get the next line from the IRC server we're connected to

        :returns: Line read from the server
        :rtype: string
        """

        data = ""
        #try:
        #    ready = select([self.irc], [], [], timeout)
        #    if ready[0]:
        #        data = self.irc.recv(BUFFER_SIZE).decode("ASCII")

        #except Exception as e:
        #    self.logger.debug("Timed out recving data %s" % str(e))
        data = self.irc.recv(BUFFER_SIZE)
        return data

    def connect_and_listen(self):
        self.joined_to_chan = False

        self.logger.debug("connecting to: " + self.serverAddr + " " + self.serverPort)

        self.irc = socket(AF_INET, SOCK_STREAM)
        # if the bot recieves no socket traffic for 5 minutes, assume that it has been disconnected
        # self.irc.settimeout(300)
        self.irc.connect((self.serverAddr, int(self.serverPort)))

        self.irc.send(("NICK %s\r\n" % self.botNick).encode("UTF-8"))
        self.irc.send(("USER %s 8 * :%s\r\n" % (self.botNick, self.botNick)).encode("UTF-8"))
        self.irc.setblocking(True)

        while True:
            data = self.get_next_line()
            self.logger.debug("Received: \"%s\"" % data.strip())
            tmp = data.split()[0]
            text = data

            # Server Directive
            debug(tmp)
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
                    temp = search("PING :[a-zA-Z0-9]+", text)
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
                debug("User message: text = %s" % text)
                user, cmd, destination = text.split()[:3]
                user = user.split('!')[0]
                message = text.split(':')[2:][0].strip()

                # TODO: May want to make this a case/switch associative array.
                if cmd == "JOIN":
                    continue

                if cmd == "KICK":
                    if message == self.botNick:
                        sleep(1)
                        self.join_channel()
                    else:
                        continue

                # if the message starts with a "!" then do something
                if message[:1] == "!":
                    try:
                        user_cmd = message[1:].split()[0] #strip the !, then give me what's after it but before the next space
                    except IndexError:
                        continue
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

class ThreadedTCPRequestHandler(BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        DataToPost = self.data[self.data.find(' :!') + 7:]
        bot.json_parser(DataToPost)

class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    pass

if __name__ == "__main__":
    ap = ArgumentParser(description="The IRC bot is the helpful little helper of UAS")
    ap.add_argument("--listen-ip", help="The IP the bot should listen on (Default: all interfaces)", default="")
    ap.add_argument("--listen-port", type=int, help="The TCP port the bot should listen on (Default: 9999)", default=9999)
    ap.add_argument("--pid-file", help="The pidfile write (Default: /opt/uas/UAS_IRC_Bot/Bot.pid)",
                    default="/opt/uas/UAS_IRC_Bot/Bot.pid")
    ap.add_argument("--conf-file", help="The config file to use (Default: /opt/uas/UAS_IRC_Bot/Unallobot.conf)",
                    default="/opt/uas/UAS_IRC_Bot/Unallobot.conf")
    ap.add_argument("--log-file", help="The log file to write (Default: /var/log/Bot.log)",
                    default="/var/log/Bot.log")
    ap.add_argument("-v", "--verbose", help="More verbose output", action="store_true")
    args = ap.parse_args()

    with open(args.pid_file, 'w') as TA:
        TA.write(str(getpid()))

    def sigterm_handle(signal, frame):
        debug('got SIGTERM')
        os.remove(args.pid_file)
        sys.exit(0)

    signal.signal(signal.SIGTERM, sigterm_handle)

    #thread for the external listener
    basicConfig(format='[%(levelname)5s] %(asctime)-15s - %(message)s')
    info("Starting the API listening service...")
    server_A = ThreadedTCPServer((args.listen_ip, args.listen_port), ThreadedTCPRequestHandler)
    server_A_thread = Thread(target=server_A.serve_forever)
    server_A_thread.setDaemon(True)
    server_A_thread.start()
        
    # instantiate the bot -- If it throws an exception, the stacktrace should be shown for troubleshooting purposes
    info("Starting the bot...")
    bot = Bot(args.conf_file, DEBUG if args.verbose else INFO,
              args.log_file)

    info("Starting the thread for the bot")
    # The IRC Part is run in a separate thread
    #server_B_thread = Thread(target=bot.connect_and_listen)
    #server_B_thread.setDaemon(True)
    #server_B_thread.start()

    bot.connect_and_listen()
    

    # we need to clean up the pid file so that the run script in init will be in the proper state    
    #os.remove('/opt/uas/UAS_IRC_Bot/Bot.pid')
