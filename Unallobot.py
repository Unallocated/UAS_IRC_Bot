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

import signal,pdb,httplib,time,glob,os,oauth2,sys

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
            self.oauth_key = config.get('Oauth','key')
            self.oauth_secret = config.get('Oauth','secret')
            #TODO: Check that all of these settings are legit before just taking them at face value
            #self.LogFile = config.get('Logging', 'logfile')
        except NoOptionError as e:
            self.logger.error("Error parsing config file: " + e.message)

        # Irc connection
        self.irc = None

        # Need this to be the value from the temp_status file on the box
        self.LastStatus = "/tmp/status"
        self.commands = self.__loadplugins__('modules/')

        self.commands['update'] = self.update

    def update(self, nothing, nothing1):

        self.commands = self.__loadplugins__('modules/')

        for module in self.commands.keys():
            reload(sys.modules[self.commands[module].__module__])

        self.commands['update'] = self.update
        self.irc.send(self.privmsg("Updated the modules."))

    def __loadplugins__(self,folder):
        function_dict = {}
        pyfiles = glob.glob(folder+'*.py')
        folder = folder.replace(os.sep,'.')
        for pyfile in pyfiles:
            if '__' in pyfile:
                continue
            pyfile = pyfile.split('/')[1].split('.')[0]
            # import file
            try:
                mod = getattr(__import__(folder+pyfile),pyfile)
                # we expect there to be a function name that matches the filename in that file we imported
                func = getattr(mod,pyfile)
                print "loaded plugin " + pyfile
                function_dict[pyfile] = func
            except:
                print "Failed to load plugin %s" % pyfile
        print "Loaded " + str(len(function_dict.values())) + " Plugins"
        return function_dict     

    def privmsg(self, msg):
        try:
            retstr = "PRIVMSG " + self.serverChan + " :" + msg + "\n"
        except Exception as e:
            retstr = "error occured - " + str(e)
        return retstr

    # This is for oauth to the website
    def build_request(self, url, method='GET'):
        params = {
            'oauth_version': "1.0",
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': int(time.time())
        }
        consumer = oauth2.Consumer(key=self.oauth_key,secret=self.oauth_secret)
        params['oauth_consumer_key'] = consumer.key

        req = oauth2.Request(method=method, url=url, parameters=params)
        signature_method = oauth2.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, consumer, None)
        return req

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

    def json_parser(self,data):
        parsed_data = loads(data)
        self.irc.send(self.privmsg(parsed_data["Service"] + ' says ' + parsed_data["Data"]))
        if (parsed_data["Service"]=="Occupancy"):
            self.LastStatus = parsed_data["Service"] + ' says ' + parsed_data["Data"]    

    def get_next_line(self):
        """
        This will get the next line from the IRC server we're connected to

        :returns: Line read from the server
        :rtype: string
        """

        data = ""
        data = self.irc.recv(BUFFER_SIZE)
        return data

    def connect_and_listen(self):
        self.joined_to_chan = False

        self.logger.debug("connecting to: " + self.serverAddr + " " + self.serverPort)

        self.irc = socket(AF_INET, SOCK_STREAM)
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
                temp = search("PING :[a-zA-Z0-9]+", data)
                if temp:
                    pong = temp.group(0)[6:]
                    self.ping(pong)
                    if self.joined_to_chan != True:
                        self.join_channel()
                        self.joined_to_chan = True
                self.ping("PONG")


            # We use continues when we know we no longer need to process anything
            elif tmp == "NOTICE":
                continue

            #user message
            else:
                debug("User message: text = %s" % text)
                user, cmd, destination = text.split()[:3]

                # TODO: May want to make this a case/switch associative array.
                if cmd == "JOIN":
                    continue

                if cmd == "MODE":
                    continue

                if cmd == "KICK":
                    if message == self.botNick:
                        sleep(1)
                        self.join_channel()
                    else:
                        continue

                user = user.split('!')[0]
                message = text.split(':')[2:][0].strip()

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
                        try:
                            self.commands[user_cmd](self,argument) # Run the function in self.commands that corresponds to the user_cmd
                        except Exception as e:
                            self.irc.send(self.privmsg("The Module errored out." + str(e)))
                        self.logger.debug("user " + user + ' issued command ' + user_cmd + " recieved with arg " + argument)

                    # invalid command - print help message
                    else:
                        self.commands['helpme'](self,'')
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
    os.remove('/opt/uas/UAS_IRC_Bot/Bot.pid')
