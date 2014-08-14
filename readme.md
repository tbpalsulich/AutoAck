AutoAck
=======

IRC bot created for the JPL DARPA XDATA team chatroom.

\#gitpush

Command line usage:
-------------------
```
usage: autoack.py [-h] [-n NICK] [-s SERVER] [-q QUIET] [-p PORT] channel

An IRC bot used to respond to keywords automatically.

positional arguments:
  channel               Channel to connect to.

optional arguments:
  -h, --help            show this help message and exit
  -n NICK, --nick NICK  Username of the bot
  -s SERVER, --server SERVER
                        Server to connect to
  -q QUIET, --quiet QUIET
                        Default number of seconds to stay quiet when told
  -p PORT, --port PORT  Port to use when connecting to the server.
```

Bot commands:
-------------
```
   AutoAck: learn [key] [value] (learn to say [value] after [key])
   AutoAck: forget [key] (forget user learned keyword [key])
   AutoAck: quiet [seconds] (don't talk for optional number of [seconds])
   AutoAck: speak (override a previous quiet command)
   AutoAck: list (print list of available keywords)
   AutoAck: blame [key] (show user who created [key])
```