#!/usr/bin/python
#Unallobot
# Uses Python 2.7.2

import socket

def ping(): # Responding to Server Pings
	ircsock.send("PONG :Pong\n")

def sendmsg (chan):
	ircsock.send("PRIVMSG "+ chan +" :" + msg + "\n")

def Eightball (data):
	if data!='' and '?' in data:
	        return choice(['It is certain.','It is decidedly so.','Without a doubt.','Yes. definitely.','You may rely on it.','As I see it, yes.','Most likely.','Outlook good.','Signs point to yes.','Yes.','Reply hazy, try again.','Ask again later.','Better not tell you now.','Cannot predict now.','Concentrate and ask again.','Don\'t count on it.','My reply is no.','My sources say no.','Outlook not so good.','Very doubtful.','Run Away!']) 
	else:
		return 'I can do nothing unless you ask me a question....'

def Address ():
	return "512 Shaw Court #105, Severn, MD 21144"

def Sign (data): # Check the sign message or Change the sign Message

def Status (): # Check the Status of the space

def Help (data):
	        data=data.replace('.','')
        helps={
                'status':'!status returns the current status of the space. (open/closed)',
                'sign':'!sign returns or updates the text displayed on the prolite LED sign.',
                'tweet':'!tweet returns the latest tweet on the @Unallocated twitter account.',
                'site':'!site returns the latest blog post on http://unallocatedspace.org/',
                'rollcall':'!rollcall lists Unallocated Space members that have checked into the space with their UAS member smart cards during the current session (opening to closing)',
                'weather':'!weather returns the weather conditions outside the space.',
                'address':address(None),
                'wiki':'!wiki when used with text returns a link most closely related to the search term on the Unallocated Wiki.',
                'link':'!link returns various links to Unallocated Space related web pages. List can be altered here: http://www.unallocatedspace.org/wiki/Links',
                'video':'!video queries the Unallocated Space youtube account and returns the top result.',
                }
	if data in helps:
		return helps[data]
	elif data in help_alias and help_alias[data] in helps:
		ret="!%s is an alias. "%data
		return ret+helps[help_alias[data]]
	else:
		return 'Available commands are: !'+' !'.join(helps.keys())

	
