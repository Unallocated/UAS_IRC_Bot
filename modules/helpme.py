def helpme(self,msg):
    keyslist=""
    self.irc.send(self.privmsg('Here is a list of valid commands: \n'))
    for keys in self.commands:
        if keys != 'JSON':
            keyslist = keyslist +'!' + keys + ', '
    self.irc.send(self.privmsg(keyslist))

