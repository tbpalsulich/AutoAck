'''
Copyright 2014 Tyler Palsulich

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

# This bot is a result of a tutoral covered on http://shellium.org/wiki.
import socket
import sys
import argparse
import atexit
import shelve
from datetime import datetime
from datetime import timedelta

# imports for Twitter functionality
import ConfigParser
import json

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API

from nltk.chat import eliza

# Time used to prevent sending messages while in quiet mode.
can_send_after = datetime.now()

# Beginning of Twitter variables
config = ConfigParser.ConfigParser()
config.read('.twitter')

consumer_key = config.get('apikey', 'key')
consumer_secret = config.get('apikey', 'secret')
access_token = config.get('token', 'token')
access_token_secret = config.get('token', 'secret')
stream_rule = config.get('app', 'rule')
account_screen_name = config.get('app', 'account_screen_name').lower() 
account_user_id = config.get('app', 'account_user_id')

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
twitterApi = API(auth)

chatbot = eliza.Chat(eliza.pairs)
# End of Twitter variables


# Check whether the given string is a positive number.
# Based on http://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-in-python.
def is_positive_number(s):
    try:
        s = float(s)
        return s > 0
    except ValueError:
        return False

# Respond to a PING from the server.
def pong(data):
  ircsock.send("PONG " + data.split()[1] + "\n")  

# Send a message to the connected server.
def send(message, user = None, force = False):
  if datetime.now() > can_send_after:
    if user is None:
      ircsock.send("PRIVMSG " + args.channel + " :" + message + "\n")
    else:
      ircsock.send("PRIVMSG " + args.channel + " :" + user + ": " + message + "\n")

# Join the given channel.
def join_channel(channel):
  ircsock.send("JOIN " + channel + "\n")

# Respond to any keywords from the map `commands` in the string `message`.
def handle(message, commands):
  for key in commands:
    if key in message:
      send((commands[key][0] + " ") * message.count(key, 0))

# Store the given key and value in the user_commands map. But, do not
# allow the users to change default commands.
def learn(key, value, user):
  if key not in default_commands:
    if key in user_commands:
      send("Relearned " + key)
    else:
      send("Learned " + key)
    user_commands[key] = [" ".join(value), user]
  else:
    send("Go away, " + user + "!")

# Forget the user command with the given key.
def forget(key):
  if key in default_commands:
    send("No.")
  elif key in user_commands:
    user_commands.pop(key) 
    send("Dropped like a bad habit.")
  else:
    send("Maybe you're the one forgetting...")

# Monitor the user account for the given twitter account.
# Auto-reply Ack to any tweet to that user stream
# https://dev.twitter.com/docs/streaming-apis/streams/user
class ReplyToTweet(StreamListener):
    def on_data(self, data):
        print data
        tweet = json.loads(data.strip())
        
        retweeted = tweet.get('retweeted')
        from_self = tweet.get('user',{}).get('id_str','') == account_user_id

        if retweeted is not None and not retweeted and not from_self:

            tweetId = tweet.get('id_str')
            screenName = tweet.get('user',{}).get('screen_name')
            tweetText = tweet.get('text')

            #chatResponse = chatbot.respond(tweetText)

            replyText = '@' + screenName + ' ' + 'ACK ' + tweetText #This could be chatResponse but for now is just ACK

            #check if repsonse is over 140 char
            if len(replyText) > 140:
                replyText = replyText[0:137] + '...'

            print('Tweet ID: ' + tweetId)
            print('From: ' + screenName)
            print('Tweet Text: ' + tweetText)
            print('Reply Text: ' + replyText)

            # If rate limited, the status posts should be queued up and sent on an interval
            twitterApi.update_status(replyText, tweetId)

    def on_error(self, status):
        print status

def send_help():
  send("Available commands:")
  send("   " + args.nick + ": autotweet (monitor the defined twitter account and AutoAck Tweets)")
  send("   " + args.nick + ": blame [key] (show user who created [key])")
  send("   " + args.nick + ": forget [key] (forget user learned keyword [key])")
  send("   " + args.nick + ": help (print this help message)")  
  send("   " + args.nick + ": learn [key] [value] (learn to say [value] after [key])")
  send("   " + args.nick + ": list (print list of available keywords)")
  send("   " + args.nick + ": quiet [seconds] (don't talk for optional number of [seconds])")
  send("   " + args.nick + ": speak (override a previous quiet command)")
  send("   " + args.nick + ": tweet (send a tweet to the defined twitter account)")
  
# Loop forever, waiting for messages to arrive.
def main_loop():
  global can_send_after
  while 1:
    message = ircsock.recv(2048) # Receive data from the server.
    message = message.strip('\n\r') # Remove any unnecessary linebreaks.

    print message

    if "PING :" in message: pong(message)

    # Only respond to chat from the current chatroom (not private or administrative log in messages).
    if splitter not in message: continue

    # Get the content of the message.
    user = message.split("!")[0][1:]
    message = message.split(splitter)[1]

    # Convert to lowercase and split the message based on whitespace.
    split = message.lower().split()

    if split[0] == args.nick.lower() + ":":   # Command addressed to the bot (e.g. learn or forget).
      if split[1] == "learn" and len(split) > 2:
        learn(split[2], message.split()[3:], user)
      elif split[1] == "forget" and len(split) == 3:
        forget(split[2])
      elif split[1] == "help":
        send_help()
      elif split[1] == "quiet" and len(split) == 2:
        can_send_after = datetime.now() + timedelta(seconds=args.quiet)
        send("Whatever you say.", user, True)
      elif split[1] == "quiet" and len(split) == 3 and is_positive_number(split[2]):
        can_send_after = datetime.now() + timedelta(seconds=int(split[2]))
        send("Whatever you say.", user, True)
      elif split[1] == "speak" and len(split) == 2:
        can_send_after = datetime.now()
      elif split[1] == "list" and len(split) == 2:
        send("Builtin commands: [" + ", ".join(default_commands) + "]")
        send("User commands: [" + ", ".join(user_commands) + "]")
      elif split[1] == "blame" and len(split) == 3:
        if split[2] in default_commands:
          send(split[2] + " is a default command.", user)
        elif split[2] in user_commands:
          send(split[2] + " was created by " + user_commands[split[2]][1], user)
        else:
          send("That's not a valid keyword!", user)
      elif split[1] == "autotweet" and len(split) > 2:
        streamListener = ReplyToTweet()
        twitterStream = Stream(auth, streamListener)
        twitterStream.userstream(_with='user')
      else:
        send("How may I help you?", user)
    else:   # Only handle messages that aren't sent directly to the bot.
      handle(message.lower(), default_commands)
      handle(message.lower(), user_commands)

if __name__ == '__main__':
    try:
      parser = argparse.ArgumentParser(description='An IRC bot used to respond to keywords automatically.')
      parser.add_argument('-n', '--nick',    default='AutoAck',           help='Username of the bot')
      parser.add_argument('-s', '--server',  default='chat.freenode.net', help='Server to connect to')
      parser.add_argument('-q', '--quiet',   default=30,   type=int,      help='Default number of seconds to stay quiet when told')
      parser.add_argument('-p', '--port',    default=6667, type=int,      help='Port to use when connecting to the server.')
      parser.add_argument('channel',                                      help='Channel to connect to.')

      args = parser.parse_args()

      # If the channel name doesn't start with a '#', prepend one.
      if args.channel[0] != "#": args.channel = "#" + args.channel

      # Substring used to split the received message into the actual message content
      splitter = "PRIVMSG " + args.channel + " :"

      # Map from keywords to how the bot will respond in chat.
      default_commands = {
                  "ack":  ["ack", args.nick],
                  "git":  ["#gitpush", args.nick],
                  "aye":  ["aye, mate!", args.nick],
                  "+1":   ["+1", args.nick],
                  "boom": ["kaboom!!!", args.nick],
                  "beum": ["kabeum!!!", args.nick],
                  "bewm": ["ba-bewm!!!", args.nick],
                  "seen": ["seen like an eaten jelly bean", args.nick]}

      # Map where chatroom members can have the bot "learn" commands.
      user_commands = shelve.open("autoack.shelf")

      # Connect to the server.
      ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      print("Attempting to connect to " + args.server + ":" + args.channel + " on port " + str(args.port) + " with username " + args.nick)
      ircsock.connect((args.server, args.port)) # Connect to the server.
      ircsock.send("USER " + args.nick + " " + args.nick + " " + args.nick + " :.\n") # Authenticate the bot.
      ircsock.send("NICK " + args.nick + "\n") # Assign the nickname to the bot.

      join_channel(args.channel)

      atexit.register(user_commands.close)
      main_loop()
    except KeyboardInterrupt:
      print >> sys.stderr, '\nExiting by user request.\n'
      sys.exit(0)
