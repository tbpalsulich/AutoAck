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
from datetime import datetime

# Check if we need to print help.
if len(sys.argv) == 1 or len(sys.argv) > 4 or sys.argv[1].find("#") != 0:
  print("Usage: python autoack.py #channel [nick [server]]")
  sys.exit()

# Variables for how to connect the bot.
channel = sys.argv[1] # Channel
botnick = "AutoAck" if len(sys.argv) < 3 else sys.argv[2] # Nickname
server = "chat.freenode.net" if len(sys.argv) < 4 else sys.argv[3] # Server
port = 6667 # Port to connect on.

# Substring used to split the received message into the actual message content
splitter = "PRIVMSG " + channel + " :"

# Time used to prevent sending messages while in quiet mode.
can_send_after = datetime.now()

# Map from keywords to how the bot will respond in chat.
default_commands = {
            "ack":  "ack",
            "git":  "#gitpush",
            "aye":  "aye, mate!",
            "+1":   "+1",
            "boom": "kaboom!!!",
            "beum": "kabeum!!!",
            "bewm": "ba-bewm!!!",
            "seen": "seen like an eaten jelly bean"}

# Map where chatroom members can have the bot "learn" commands.
user_commands = {}

# Respond to a PING from the server.
def pong(data):
  ircsock.send("PONG " + data.split()[1] + "\n")  

# Send a message to the connected server.
def send(message):
  if datetime.now() > can_send_after:
    ircsock.send("PRIVMSG " + channel + " :" + message + "\n")

def join_channel(channel):
  ircsock.send("JOIN " + channel + "\n")

# Respond to any keywords from the map `commands` in the string `message`.
def handle(message, commands):
  for key in commands:
    if key in message:
      send((commands[key] + " ") * message.count(key, 0))

# Store the given key and value in the user_commands map. But, do not
# allow the users to change default commands.
def learn(key, value):
  if key not in default_commands:
    if key in user_commands:
      send("Relearned " + key)
    else:
      send("Learned " + key)
    user_commands[key] = " ".join(value)
  else:
    send("Go away!")

# Forget the user command with the given key.
def forget(key):
  if key in default_commands:
    send("No.")
  elif key in user_commands:
    user_commands.pop(key) 
    send("Dropped like a bad habit.")
  else:
    send("Maybe you're the one forgetting...")

def send_help():
  send("Available commands:")
  send("   " + botnick + ": learn [key] [value]")
  send("   " + botnick + ": forget [key]")

# Connect to the server.
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Attempting to connect to " + server + ":" + channel + " on port " + str(port) + " with username " + botnick)
ircsock.connect((server, port)) # Connect to the server using port 6667.
ircsock.send("USER " + botnick + " " + botnick + " " + botnick + " :.\n") # Authenticate the bot.
ircsock.send("NICK " + botnick + "\n") # Assign the nickname to the bot.

join_channel(channel)

# Loop forever, waiting for messages to arrive.
while 1:
  message = ircsock.recv(2048) # Receive data from the server.
  message = message.strip('\n\r') # Remove any unnecessary linebreaks.

  print(message)

  if "PING :" in message: pong(message)

  # Only respond to chat from the current chatroom (not private or administrative log in messages).
  if splitter not in message: continue

  # Get the content of the message.
  message = message.split(splitter)[1]

  # Convert to lowercase and split the message based on whitespace.
  split = message.lower().split()

  if split[0] == botnick.lower() + ":":   # Command addressed to the bot (e.g. learn or forget).
    if split[1] == "learn" and len(split) > 2:
      learn(split[2], message.split()[3:])
    if split[1] == "forget":
      forget(split[2])
    if split[1] == "help":
      send_help()
    if split[1] == "quiet":
      can_send_after = datetime.now() + datetime.timedelta(seconds=30)
  else:   # Only handle messages that aren't sent directly to the bot.
    handle(message.lower(), default_commands)
    handle(message.lower(), user_commands)
