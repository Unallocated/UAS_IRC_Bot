import urllib2

def trafficlight(self,msg):
    req = urllib2.Request('http://10.0.1.249:8080/',
        headers = self.trafficlight_headers,
        data = '{"stoplight":'+msg+'}'
    )
    try:
        f = urllib2.urlopen(req, timeout = self.trafficlight_timeout)
        print f.read()
        print "after response was printed"
    except urllib2.URLError, e:
        print "URLError thrown", e
