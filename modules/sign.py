import httplib

def sign(self, data):
    # Check the sign message or Change the sign Message
    connection = httplib.HTTPConnection('10.0.0.3:8080')
    data = '{"message":"%s","color":"green","transition":"none"}' % data
    connection.request('POST','/message/new',data)
    response = connection.getresponse().read()
    self.irc.send(self.privmsg("Updated Sign - " + response))
   

if __name__ == "__main__":
    print "hi"
    sign(None,'hello')
