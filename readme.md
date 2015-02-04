AutoAck
=======

IRC bot created for the JPL DARPA XDATA team chatroom.

\#gitpush

Install
=======

1. git clone git@github.com:tpalsulich/AutoAck.git
2. virtualenv venv
3. . venv/bin/activate
2. pip install -r requirements.txt
3. cp -R .twitter.sample .twitter
4. cp -R .facebook.sample .facebook
5. edit .twitter file and add in your API key for twitter and other params
6. edit .facebook file and add in your access token

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
   AutoAck: autotweet (send a tweet to the defined Twitter account)
   AutoAck: autofbook (post a message to the defined Facebook account)
   AutoAck: help (print this help message)
```

Run persistently:
-----------------
Install `supervisord` by running `[sudo] easy_install supervisord`. Then edit
the `command=...` line in the config file `supervisord.conf` to enter the proper
channel, server, port, etc. Then start the daemon by running
```
supervisord -c ./supervisord.conf
```

Contributing:
-------------
All pull requests, feature requests, bug reports, and questions are welcome!
If you want to contribute, fork, branch, commit, and send a pull request!
[Here](https://gun.io/blog/how-to-github-fork-branch-and-pull-request/) is a
good tutorial on this git workflow.
