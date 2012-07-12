# -*- coding: utf-8 -*-
# flacker
# Copyright: (c) 2012 Christoph Heer
# License: BSD


from flaskext.script import Manager, Server, Shell

from flacker import app, redis

def _make_context():
    return dict(app=app, redis=redis)

manager = Manager(app)
manager.add_command("shell", Shell(make_context=_make_context))
manager.add_command("runserver", Server())

@manager.command
def add_torrent(info_hash):
    redis.sadd('torrents', info_hash)
    print "Torrent added"

if __name__ == '__main__':
    manager.run()