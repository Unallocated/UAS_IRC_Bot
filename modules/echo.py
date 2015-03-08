def echo(self, msg):
    self.irc.send(self.privmsg(msg))
