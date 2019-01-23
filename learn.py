#!/usr/bin/env python3

import sys
import json

class App():
    def run(self):
        db = json.loads(open('db.json', 'rt').read())

        for word in db.keys():
            if db[word] != '?':
                continue
            self.learn(word)

    def learn(self, word):
        print(word)

if __name__ == '__main__':
    app = App()
    sys.exit(app.run())
