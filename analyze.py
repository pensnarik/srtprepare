#!/usr/bin/env python3

import os
import sys
import tty
import json
import datetime as dt

try:
    import msvcrt
    getch = msvcrt.getch
except:
    import sys, tty, termios
    def _unix_getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def prepare(filename):
    state = 'looking_for_id'
    buffer = list()

    for line in open(filename, 'rt', encoding='utf-8', errors='ignore').readlines():
        message = line.strip()
        if state == 'looking_for_id':
            if message == '':
                continue
            else:
                id = message
                state = 'looking_for_time'
        elif state == 'looking_for_time':
            time = message
            state = 'looking_for_text'
        elif state == 'looking_for_text':
            if message != '' and not (message.startswith('<')):
                buffer.append(message)
            else:
                state = 'looking_for_id'

    return ' '.join(buffer).lower()


getch = _unix_getch

if len(sys.argv) < 2:
    print("Usage: analyze.py <filename>")
    sys.exit(1)

state = 'searching_word'
data = prepare(sys.argv[1])
db = json.loads(open('db-new.json', 'rt').read())

words = []

replacemap = [["who's", "who is"], ["'l", " will"], ["'re", " are"], ["don't", "do not"], ["it's", "it is"],
              ["haven't", "have not"], ["didn't", "did not"], ["i'm", "i am"], ["i'd", "i would"],
              ["should've", "should have"], ["that's", "that is"], ["doesn't", "does not"],
              ["hadn't", "had not"], ["wasn't", "was not"], ["i've", "i have"], ["'cause", "because"],
              ["could've", "could have"], ["you've", "you have"], ["isn't", "is not"],
              ["why'd", "why would"], ["'s", ""], ["'ve", " have"], ["n't", " not"]]
buffer = ''

for r in replacemap:
    data = data.replace(r[0], r[1])

for c in data:
    if c.isalpha():
        buffer = buffer + c
        state = 'reading_word'
    else:
        if state == 'reading_word':
            words.append(buffer)
            buffer = ''
            state = 'searching_word'
        else:
            # Skip non-alpha char
            pass

stat = dict()

for word in words:
    stat.update({word: stat.get(word, 0) + 1})

s = sorted([[w, c] for w, c in stat.items() if len(w) > 3], key=lambda x: x)

# print('\n'.join('%s: %s' % (i[0], i[1]) for i in s))

new_words = 0
total_words = 0

for word in s:
    if word[0] not in db.keys():
        new_words += 1
    total_words += 1

print("Total words: %s, new words: %s" % (total_words, new_words))

current_index = 0

def getnextword(pos=1):
    global current_index
    current_index = current_index + pos
    if current_index < 0:
        current_index = 0
    if current_index > len(s) - 1:
        return None
    return s[current_index][0]

def get_context(word):
    for line in open(sys.argv[1], 'rt', encoding='utf', errors='ignore').readlines():
        if word.lower() in line.lower():
            return line.strip()
    return '<Not found>'

pos = 1

while True:
    word = getnextword(pos)
    if word is None:
        print("End of the list has been reached")
        sys.exit(0)
    if word in db.keys() and pos > 0:
        continue
    pos = 1
    print(word)
    ch = ''
    while ch not in ('W', 'N', 'Y', '?', 'Q', 'B', 'C'):
        print("[W] Not a word, [N] Name, [Y] Known word, [?] Not a known word, [B] Back, [C] Context, [Q] Exit: ")
        ch = getch().upper()
    if ch == 'Q':
        sys.exit(0)
    if ch == 'B':
        pos = -1
        continue
    if ch == 'C':
        print(get_context(word))
        pos = 0
        continue
    db.update({word: {'status': ch,
               'source': os.path.basename(sys.argv[1]),
               'dt': dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}})
    with open('db-new.json', 'wt') as f:
        f.write(json.dumps(db, indent=4, sort_keys=True))
