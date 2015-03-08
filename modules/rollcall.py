import pdb
import urllib2

def rollcall(self,msg):
    with open(self.checkin_file,'r') as checkin:
        users = ''.join(checkin.readlines())
    msg = "The following users have checked in: " + users
    self.irc.send(self.privmsg(msg))    

#def checkin(self,msg):
#    pdb.set_trace()
#    with open(self.checkin_file,'r') as checkin:
#        users = ''.join(checkin.readlines())
#    msg = "The following users have checked in: " + users
#    self.irc.send(self.privmsg(msg))
#    request = self.build_request(self,)
#    lines = urllib2.urlopen(request.to_url()).readlines()
#
#    # We are waiting for r00ster to finish this
    
