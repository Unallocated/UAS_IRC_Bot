#UAS_IRC_Bot
===========

The new Unallocated Space IRC Bot

Utilize UnalloBot3.conf to setup connection information using the template UnalloBot3.conf

Commands:
* !eightball or !8ball
* !site
* !address
* !status
	
More will be implemented as time goes on!

To be Implemented
* !sign
* !rollcall
* Extend functionality and code cleanup
* Auto Re-join Channel & Auto Re-Connect 
* add cli parsing for verbose (debug info), path to config (with default)
* optionally print info to stderr, always logfile, and detach as daemon (no stderr in that case)
* Try + Catch error handling
* Implement Lavenstein
* Break find command section into its own function
* Data Validation in self.privmsg
* Figure out why the bot thinks everything pronto says is wrong
* Setup Ping to verify server uptime and switch servers if banned/server down
* Input Validation
* Daemonization
* Clean Exit
* Logging to a file

API - JSON
*	Service - String
*	Key - Assigned Key for accessing the bot posting capability
*	Data - String

example in bash:
	nc 127.0.0.1 9999 !JSON {"Service":"Checkin","Key":"1s2d3fq","Data":"Forgotten has checked into the space"} 
