import random
# this function is formatted like dog doo-doo - Crypt0s
def eightball(self, data):
    if data != '' and '?' in data:
            self.irc.send(self.privmsg(random.choice(['It is certain.',
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

