#!/bin/sh
wget -O irclib.zip http://sourceforge.net/projects/python-irclib/files/irc-0.7.zip/download || curl -o irclib.zip http://sourceforge.net/projects/python-irclib/files/irc-0.7.zip/download
unzip irclib.zip
rm irclib.zip
mv irc-0.7/irc .
rm -r irc-0.7
