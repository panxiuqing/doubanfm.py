# coding=utf-8
#!/usr/bin/env python

#api_string = 'http://www.douban.com/j/app/radio/people?app_name=radio_desktop_win&version=100&user_id=&expire=&token=&sid=&h=&channel=1&type=n'

import curses
import subprocess
import urllib, urllib2, json
import tempfile
import locale
import mplayer
import time
import threading

#locale
locale.setlocale(locale.LC_CTYPE, '')
code = locale.getpreferredencoding()

#GET request value
app_name = 'radio_desktop_win'
version = '100'
user_id = ''
expire = ''
token = ''
sid = ''
h = ''
channel = '1'
Type = 'n'

fm_url = 'http://www.douban.com/j/app/radio/people?'
get_list = [('app_name=', app_name),
            ('version=', version),
            ('user_id=', user_id),
            ('expire=', expire),
            ('token=', token),
            ('sid=', sid),
            ('h=', h),
            ('channel=', channel),
            ('type=', Type)]

# ncurses UI code
win = curses.initscr()
curses.noecho()
curses.cbreak()

## use color
if curses.has_colors():
    curses.start_color()

curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)

curses.init_pair(13, curses.COLOR_CYAN, curses.COLOR_BLACK)

## left window
l_begin_x = 0 ; l_begin_y = 0
l_height = 24; l_width = 29
l_win = curses.newwin(l_height, l_width, l_begin_y, l_begin_x)
l_win.keypad(1)
l_win.border(0)

l_title = "channel"
channels = {2: {'华语': 1},
            4: {'欧美': 2},
            6: {'八零': 4},
            8: {'咖啡': 32},
            10: {'轻音乐': 9},
            12: {'新歌': 61},
            14: {'粤语': 6},
            16: {'九零': 5},}

l_win.addstr(l_title.encode(code), curses.A_BOLD)

### channel list in l_win
for idx in channels:
    l_win.addstr(idx, 2, channels[idx].keys()[0] + ' MHz', curses.color_pair(1))

l_win.refresh()

## right window
r_begin_x = 30; r_begin_y = 0
r_height = 16; r_width = 49
r_win = curses.newwin(r_height, r_width, r_begin_y, r_begin_x)
r_win.border(0)

r_title = "Playing"
r_win.addstr(r_title.encode(code), curses.A_BOLD)
r_win.addstr(14, 30, "加红心")
r_win.addstr(14, 40, "下一首")

# Player
p = mplayer.Player()

# play function
def play_channel(url):
    img_file = tempfile.NamedTemporaryFile()
    resp = urllib2.urlopen(url)
    play_list = json.loads(resp.read())['song']
    for mp3 in play_list:
        img_url = mp3['picture']
        urllib.urlretrieve(img_url, img_file.name)
        mp3_title = mp3['title'].encode(code)
        mp3_info = (mp3['albumtitle'] + '\n' + mp3['artist'])
        subprocess.call(['notify-send', '-i', img_file.name, mp3_title, mp3_info])
        r_win.addstr(2, 2, mp3['artist'].encode(code), curses.A_BOLD)
        r_win.addstr(3, 2, mp3['albumtitle'].encode(code))
        r_win.addstr(5, 2, mp3_title)
        r_win.refresh()
        p.loadfile(mp3['url'])
        time.sleep(mp3['length'])
        if td_flags[threading.currentThread().getName()]:
            return

# play_channel when open
url = fm_url + "&".join(key + value for key , value in get_list)
td = threading.Thread(target = play_channel, args = (url,))
td.start()
td_flags = {td.name: False}     #exit a thred
#play_channel(url)
l_win.move(2, 2)

while l_win.getyx()[1] == 2:
    ch = l_win.getch()
    cursor_y = l_win.getyx()[0]
    if ch == ord('j'):
        if cursor_y < 16:
            l_win.move(cursor_y + 2, 2)
        else:
            continue
    elif ch == ord('k'):
        if cursor_y > 2:
            l_win.move(cursor_y - 2, 2)
        else:
            continue
    elif ch == ord('p'):
        channel = channels[cursor_y].values()[0]
        url = fm_url + "&".join(key + value for key , value in get_list)
        p.stop()
        td_flags[td.name] = True
        td = threading.Thread(target = play_channel, args = (url,))
        td.start()
        td_flags[td.name] = False
        #play_channel(url)
    else:
        break

curses.endwin()
