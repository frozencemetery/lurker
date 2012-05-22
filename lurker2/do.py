# Copyright (C) 2012 Robbie Harwood
# Based on code from the python irclib python-irclib.sourceforge.net (GPL)

    # This file is part of lurker.

    # lurker is free software: you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.

    # lurker is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details.

    # You should have received a copy of the GNU General Public License
    # along with lurker.  If not, see <http://www.gnu.org/licenses/>.


# to find the first instance of a hostmask:
#     re.search("(?<=" + nick + " \().*?(?=\) joined)", bluh).group(0)
# Note that this isn't a good whois because it's first only

def coff(f): # moderately naive method to get celsius from fahrenheit
    return (int((f-32)*(500.0)/(9.0)))/100.0

def command(self, e, cmd, c, nick):
    executed = 0
    channel = e.target()
    if channel[:1] != "#" and channel[:1] != "&" and channel[:1] != "+" and channel[:1] != "!": # checking for private queries and responding accordingly
        channel = nick
    if nick == "frozencemetery": # my commands.
        if cmd[:5] == "nick ":
            cmd = cmd.split(" ", 1)[1]
            c.nick(cmd)
            executed = 1
        elif cmd[:9] == "broadcast":
            executed = 1
            import random
            s = cmd.split(" ", 2)
            if len(s) != 3:
                c.privmsg(nick, "Parsing error on token: " + cmd)
                f.write("Parsing error on token: " + cmd)
            else:
                t = s[2].split("d", 1)
                if len(t) != 2:
                    c.privmsg(nick, "Parsing error on token: " + cmd)
                    f.write("Parsing error on token: " + cmd)
                else :
                    testa = t[1].split("+", 1) #
                    testb = t[1].split("-", 1) #
                    if len(testa[0]) > len(testb[0]):
                        numtoroll = int(t[0])
                        sidenum = int(testb[0])
                        bonus = -int(testb[1])
                    elif len(testa[0]) < len(testb[0]):
                        numtoroll = int(t[0])
                        sidenum = int(testa[0])
                        bonus = int(testa[1])
                    else: # the two were equal; in other words, no bonus
                        numtoroll = int(t[0])
                        sidenum = int(testa[0])
                        bonus = 0
                    if numtoroll < 1:
                        numtoroll = 1
                    if sidenum <2:
                        counter = numtoroll
                    else :
                        counter, i = 0, 0
                        while i < numtoroll:
                            roll = random.randint(1, sidenum);
                            counter = counter + roll;
                            i = i + 1;
                    counter = counter + bonus
                    c.privmsg(s[1], nick + " rolled a " +str(counter))
        if cmd == "disconnect":
            self.disconnect()
            executed = 1
        if cmd == "test":
            c.privmsg(channel, e.source())
            executed = 1
        elif cmd == "die":
            self.die()
            executed = 1
        elif cmd[:4] == "join":
            z = cmd.split(" ", 1) 
            disp = z[1].split(" ", 1) 
            c.join(z[1])
            executed = 1
        elif cmd[:3] == "say":
            z = cmd.split(" ", 2)
            c.privmsg(z[1], z[2])
            executed = 1
        elif cmd[:6] == "action":
            z=cmd.split(" ", 2) 
            c.action(z[1], z[2])
            executed = 1
    # commands for all
    if cmd[:4] == "roll": 
        executed = 1
        import random
        s = cmd.split(" ", 1) 
        if len(s) != 2:
            c.privmsg(channel, "Syntax is: \"roll xdy[\xc2z]\".")
            # \xc2 is the plusorminus character
        else:
            t = s[1].split("d", 1) 
            if len(t) != 2:
                c.privmsg(channel, "Syntax is: \"roll xdy[\xc2z]\".")
            else :
                testa = t[1].split("+", 1) #
                testb = t[1].split("-", 1) #
                if len(testa[0]) > len(testb[0]):
                    numtoroll = int(t[0])
                    sidenum = int(testb[0])
                    bonus = -int(testb[1])
                elif len(testa[0]) < len(testb[0]): #testa's split is better
                    numtoroll = int(t[0])
                    sidenum = int(testa[0])
                    bonus = int(testa[1])
                else: # the two were equal; in other words, no bonus
                    numtoroll = int(t[0])
                    sidenum = int(testa[0])
                    bonus = 0
                if numtoroll < 1:
                    numtoroll = 1
                if sidenum <2:
                    counter = numtoroll
                else :
                    counter, i = 0, 0
                    while i < numtoroll:
                        roll = random.randint(1, sidenum);
                        counter = counter + roll;
                        i = i + 1;
                counter = counter + bonus
                if nick != "robbie" and channel == nick:
                    c.privmsg("robbie", "I rolled : " + str(counter) + " for " + nick + ".")
                c.privmsg(channel, "I rolled : " + str(counter) + " for " + nick + ".")
    elif cmd[:4] == "help":
        c.privmsg(channel, nick + ": https://paste.debian.net/plainh/47aa547e is the current version.  Bother frozencementery to make it better if it's missing something, or if you want a function you don't see there.")
    elif cmd == "hug me":
        executed = 1
        c.action(channel, "hugs " + nick + ".")
    elif cmd[:4] == "hug ":
        executed = 1
        name = cmd.split(" ", 1)[1]
        c.action(channel, "hugs " + name + ".")
    elif cmd[:3] == "fml":
        import urllib2
        import re
        response = urllib2.urlopen('http://www.fmylife.com/random')
        html = response.read()
        html = html.replace("Today and ends with FML", "")
        html = re.search("Today.*?FML", html)
        res = html.group(0)
        lst = re.findall("\<.*?>", res)
        for x in lst:
            res = res.replace(x, "")
        res = res.replace("&quot;", "\"")
        c.privmsg(channel, nick + ": " + res)
        executed = 1
    elif cmd[:2]== "fm" or cmd[:2] == "np":
        import urllib2
        import re
        import cPickle
        cmd = cmd.split(" ", 1)
        try:
            cmd = cmd[1]
            if len(cmd) >= 4 and cmd[:4] == "set ":
                cmd = cmd.split(" ", 1)
                user = cmd[1]
                ref = "../rsrc/lastfm.dict"
                lf = open(ref, "r")
                bill = cPickle.load(lf)
                lf.close()
                bill[nick] = user
                lf = open(ref, "w")
                cPickle.dump(bill, lf)
                lf.close()
            else:
                user = cmd
        except:
            ref = "../rsrc/lastfm.dict"
            lf = open(ref, "r")
            bill = cPickle.load(lf)
            user = bill[nick]
            lf.close()
        url = "http://ws.audioscrobbler.com/1.0/user/" + user + "/recenttracks.rss"
        response = urllib2.urlopen(url)
        urlload = response.read()
        m = re.search("(?<=/music/).*?(?=</link>)", urlload)
        m = m.group(0)
        m = urllib2.unquote(m)
        m = m.replace("+noredirect/", "")
        m = m.replace("+", " ")
        m = m.replace("&quot;", "\"")
        m = m.replace("%26", "&")
        ct = m.replace("/_/", " - ")
        ct = urllib2.unquote(ct)
        c.privmsg(channel, nick + ": " + ct)
    elif cmd[:2] == "fw":
        try:
            import urllib2
            import re
            import cPickle
            url = "http://thefuckingweather.com/?where="
            ref = "/Network/Servers/osxserver.b-aassoc.edu/Volumes/ServerDrive/NetUsers/robbie/lurker2/rsrc/tfw.dict"
            cmd = cmd.split(" ", 1)
            try:
                cmd = cmd[1]
                if cmd[:4] == "set ":
                    cmd = cmd.split(" ", 1)[1]
                    fw = open(ref, "r")
                    bill = cPickle.load(fw)
                    fw.close()
                    bill[nick] = cmd
                    fw = open(ref, "w")
                    cPickle.dump(bill, fw)
                    fw.close()
            except:
                fw = open(ref, "r")
                bill = cPickle.load(fw)
                fw.close()
                cmd = bill[nick]
            cmd = urllib2.quote(cmd)
            url = url + cmd
            import urllib2
            response = urllib2.urlopen(url)
            m = response.read()
            temp = int(re.search("(?<=<span class=\"temperature\" tempf=\").*?(?=\">)", m).group(0))
            location = re.search("(?<=<span id=\"locationDisplaySpan\" class=\"small\">).*?(?=</span>)", m).group(0)
            status = re.search("(?<=<p class=\"remark\">).*?(?=</p>)", m).group(0)
            paren = re.search("(?<=<p class=\"flavor\">).*?(?=</p>)", m).group(0)
            dayv = re.search("(?<=<th>DAY</th><th style=\"width:7.5em;\">).*(?=</th>)", m).group(0)
            highv = re.search("(?<=<th>HIGH</th><td class=\"temperature\" tempf=\").*(?=\r)", m).group(0)
            lowv = re.search("(?<=<th>LOW</th><td class=\"temperature\" tempf=\").*(?=\r)", m).group(0)
            fcv = re.search("(?<=<th>FORECAST</th><td>).*(?=\r)", m).group(0)

            highv = re.search("(?<=<td class=\"temperature\" tempf=\").*", highv).group(0)
            tempha = int(re.search(".*?(?=\">)", highv).group(0))
            highv = re.search("(?<=tempf=\").*", highv).group(0)
            templa = int(re.search(".*?(?=\">)", lowv).group(0))
            lowv = re.search("(?<=tempf=\").*", lowv).group(0)
            fca = re.search(".*?(?=</td>)", fcv).group(0)
            fcv = re.search("(?<=<td>).*", fcv).group(0)
            daya = re.search(".*?(?=</th>)", dayv).group(0)
            dayv = re.search("(?<=em;\">).*", dayv).group(0)
            dayb = re.search(".*?(?=</th>)", dayv).group(0)
            temphb = int(re.search(".*?(?=\">)", highv).group(0))
            templb = int(re.search(".*?(?=\">)", lowv).group(0))
            fcb = re.search(".*?(?=</td>)", fcv).group(0)

            magic = "\x02" + location + "\x0F: " + str(temp) + " F (" + str(coff(temp)) + " C) | " + status + " (" + paren + ") | " + daya + ": High " + str(tempha) + " F (" + str(coff(tempha)) + " C), Low " + str(templa) + " F (" + str(coff(templa)) + " C).  " + fca + " | " + dayb + ": High " + str(temphb) + " F (" + str(coff(temphb)) + " C), Low " + str(templb) + " F (" + str(coff(templb)) + " C).  " + fcb
            magic = magic.replace("ITS", "IT'S")
            import random
            switch = random.randint(1,20)
            if switch == 1:
                c.privmsg(channel, "IT'S RAINING MEN")
                pass
            elif switch == 2:
                c.privmsg(channel, "CHOCOLATE RAIN")
                pass
            else:
                c.privmsg(channel, magic)
                pass
        except:
            c.privmsg(channel, "Syntax is !fw <location>.  If you have invoked !fw set <location>, you may invoke !fw.")
        executed = 1
    elif cmd[:6] == "alert ":
        import time
        stof = "../rsrc/alerts.db"
        read = open(stof, "a")
        cmd = e.source() + " " + cmd.split(" ", 1)[1] 
        if len(cmd) > 380:
            cmd = cmd[:380]
        cmd += time.strftime(" at %Y:%m:%d:%H:%M:%S")
        read.write(cmd + "\n")
        read.close()
        c.privmsg(channel, "Reminder saved.")
        executed == 1
    elif cmd[:10] == "anonalert ":
        stof = "../rsrc/alerts.db"
        read = open(stof, "a")
        cmd = "<anonymous_user> " + cmd.split(" ", 1)[1]
        if len(cmd) > 380:
            cmd = cmd[:380]
        cmd += time.strftime(" at %Y:%m:%d:%H:%M:%S")
        read.write(cmd + "\n")
        read.close()
        c.privmsg(channel, "Reminder saved.")
        executed == 1
    elif cmd == "convo":
        import random
#        stof = "../rsrc/convo.db"
#        read = open(stof, 'r')
#        finalline = ""
#        numread = 0
#        for line in read:
#            numread += 1
#            prob = random.randint(1, numread);
#            if prob == 1:
#                finalline = line
#        read.close()
#        c.privmsg(channel, finalline)
        stof = "../rsrc/convo.db"
        read = open(stof, 'r')
        linecount = 0
        for line in read:
            linecount += 1
        read.close()
        choice = random.randint(0, linecount-1)
        read = open(stof, 'r')
        finalline = ""
        for line in read:
            if choice == 0:
                finalline = line
            choice -= 1
        read.close()
        c.privmsg(channel, finalline)
    elif cmd[:10] == "convo add ":
        cmd = cmd.split(" ", 2)[2]
        stof = open("../rsrc/convo.db", 'a')
        stof.write(cmd + '\n')
        stof.close()
        finalline = "NOW WE'RE HAVING A GOOD TIME RIGHT"
        c.privmsg(channel, finalline)
    elif cmd[:6] == "source":
        c.privmsg(channel, nick + ": You can find my source at https://savannah.nongnu.org/projects/lurker and BTS at https://savannah.nongnu.org/bugs/?group=lurker")
    elif cmd[:2] == "q " or cmd[:4] == "ddg " or cmd[:6] == "quack ":
        cmd = cmd.split(" ", 1)[1]
        url = "https://duckduckgo.com/html?kp=-1&q="
        import urllib
        beep = urllib.quote_plus(cmd)
        c.privmsg(channel, nick + ": " + url + beep)
    elif cmd[:4] == "test":
        c.privmsg(channel, nick + ": blargl")
        executed = 1
    elif cmd[:4] == "ping":
        c.action(channel, "squeaks at " + nick)
        executed = 1
        pass
    elif cmd == "static":
        import random
        d = random.randint(0,1)
        if d == 0:
            c.action(channel, "ssssssssssssSSSSSSSSSSSSHHHHHHHHHHHHHHHHHHHHHHHHHHHHHhsssssssssssssssssssssZachery.  Acetaminophen.  Beige.ssssssssssssSSSSSSSSSSSSHHHHHHHHHHHHHHHHHHHHHHHHHHHHHhsssssssssssssssssssss")
            pass
        else:
            c.action(channel, "performs a gymnastics move while having complete motion control the entire time, with no bursts of movement")
            pass
        executed = 1
        pass
    elif cmd[:8] == "lantunes" or cmd[:2] == "lt":
        url = "http://music.furstlabs.com"
        import urllib2
        import re
        response = urllib2.urlopen(url)
        m = response.read() 
        m = m.replace('\n', '')
        junk = re.search("(?<=<tr id=).*?(?=</tr>)", m).group(0)
        try:
            rest = re.findall("(?<=<td>).*?(?=</td>)", junk)
            title = '"' + rest[0] + '"'
            
            artist = ""
            try:
                artist = rest[1]
                if artist == "N/A":
                    artist = ""
                    pass
                else:
                    artist = " by " + artist
                    pass
                pass
            except:
                pass

            time = ""
            try:
                time = rest[3]
                if time == "N/A":
                    time = ""
                    pass
                else:
                    time = ' (' + time + ')'
                    pass
                pass
            except:
                pass

            final = title + artist + time
            c.privmsg(channel, final)
            executed = 1
            pass
        except:
            c.privmsg(channel, "noep.")
            pass
        pass        
    elif len(cmd) <= 0:
        return
    elif executed == 0:
        print "Failed."
        c.action(channel, "doesn't know how to " + cmd + ".")

def reset(command):
    return;
#    if command == ""
#        reload()
#    elif command ==""
#        reload()
