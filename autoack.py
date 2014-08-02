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

if len(sys.argv) == 1 or len(sys.argv) > 4:
  print("Usage: autoack.py #channel [nick [server]]")
  sys.exit()

channel = sys.argv[1] # Channel
botnick = "AutoAck" if len(sys.argv) < 3 else sys.argv[3] # Your bots nick
server = "chat.freenode.net" if len(sys.argv) < 4 else sys.argv[3] # Server

splitter = "PRIVMSG " + channel + " :"

default_commands = {
            "ack":  "ack",
            "git":  "#gitpush",
            "aye":  "aye, mate!",
            "+1":   "+1",
            "boom": "kaboom!!!",
            "beum": "kabeum!!!",
            "bewm": "ba-bewm!!!",
            "seen": "seen like an eaten jelly bean"}

user_commands = {}

def pong(data):
  ircsock.send("PONG " + data.split()[1] + "\n")  

def send(msg):
  ircsock.send("PRIVMSG " + channel + " :" + msg + "\n")

def join_channel(channel):
  ircsock.send("JOIN " + channel + "\n")

def handle(ircmsg, commands):
  for key in commands:
    if key in ircmsg:
      send((commands[key] + " ") * ircmsg.count(key, 0))

def learn(key, value):
  if key not in default_commands:
    user_commands[key] = " ".join(value)
    if key in user_commands:
      send("Relearned " + key)
    else:
      send("Learned " + key)
  else:
    send("Go away!")

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

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
ircsock.send("USER " + botnick + " " + botnick + " " + botnick + " :.\n") # user authentication
ircsock.send("NICK " + botnick + "\n") # here we actually assign the nick to the bot

join_channel(channel) # Join the channel using the functions we previously defined

while 1:
  ircmsg = ircsock.recv(2048) # receive data from the server
  ircmsg = ircmsg.strip('\n\r') # removing any unnecessary linebreaks.
  print(ircmsg)

  if "PING :" in ircmsg: pong(ircmsg)

  if splitter not in ircmsg: continue

  ircmsg = ircmsg.split(splitter)[1]

  split = ircmsg.lower().split()

  print split

  if split[0] == botnick.lower() + ":":
    if split[1] == "learn" and len(split) > 2:
      learn(split[2], ircmsg.split()[3:])
    if split[1] == "forget":
      forget(split[2])
    if split[1] == "help":
      send_help()
  else:
    handle(ircmsg, default_commands)
    handle(ircmsg, user_commands)
