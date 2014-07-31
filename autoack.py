# This bot is a result of a tutoral covered on http://shellium.org/wiki.
# Import some necessary libraries.
import socket 
import time

# Some basic variables used to configure the bot        
server = "chat.freenode.net" # Server
channel = "#test-ops" # Channel
botnick = "AutoAck" # Your bots nick

splitter = "PRIVMSG " + channel + " :"

def ping(data):
  ircsock.send("PONG " + data.split()[1] + "\n")  

def send(msg):
  ircsock.send("PRIVMSG " + channel + " :" + msg + "\n")

def join_channel(chan):
  ircsock.send("JOIN " + chan + "\n")

def handle(ircmsg, key, msg):
  if ircmsg.find(key) != -1:
    send ((msg + " ") * ircmsg.count(key, 0))
                  
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
ircsock.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :.\n") # user authentication
ircsock.send("NICK "+ botnick +"\n") # here we actually assign the nick to the bot

join_channel(channel) # Join the channel using the functions we previously defined

while 1: # Be careful with these! it might send you to an infinite loop
  ircmsg = ircsock.recv(2048) # receive data from the server
  ircmsg = ircmsg.strip('\n\r') # removing any unnecessary linebreaks.
  print(ircmsg) # Here we print what's coming from the server

  if ircmsg.find("PING :") != -1: # if the server pings us then we've got to respond!
    ping(ircmsg)

  if ircmsg.find(splitter) == -1:
    continue

  print ircmsg.split(splitter)
  ircmsg = ircmsg.split(splitter)[1].lower()

  handle(ircmsg, "ack", "ack")
  handle(ircmsg, "git", "#gitpush")
  handle(ircmsg, "aye", "aye, mate!")
  handle(ircmsg, "+1", "ack, +1")
  handle(ircmsg, "boom", "Kaboom!!!")
  handle(ircmsg, "beum", "Kabeum!!!")
  handle(ircmsg, "bewm", "Ba-bewm")