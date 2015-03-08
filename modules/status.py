def status(self, data):        # Check the Status of the space
    try:
        with open('/tmp/status') as statusfile:
            statusMsg = statusfile.readlines()
        statusMsg = ''.join(statusMsg).strip()
    except:
        statusMsg = "An error occured when attempting to read the status"
    self.irc.send(self.privmsg(statusMsg))
    #self.irc.send(self.privmsg(self.LastStatus))

