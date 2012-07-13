# -*- coding: utf-8 -*-
# flacker
# Copyright: (c) 2012 Christoph Heer
# License: BSD

import os
import shutil
from datetime import datetime
from hashlib import sha1
from binascii import b2a_hex

from bencode import bencode, bdecode
from flask import current_app
from flaskext.script import Manager, Server, Shell

from flacker import app, redis

def _make_context():
    return dict(app=app, redis=redis)

def _exist_torrent(info_hash):
    return redis.sismember('torrents', info_hash)

def _add_torrent(name, info_hash, torrent_file_path=None):
    if _exist_torrent(info_hash):
        return False
    
    redis.sadd('torrents', info_hash)
    
    torrent_key = 'torrent:%s' % info_hash
    redis.hset(torrent_key, 'name', name)
    redis.hset(torrent_key, 'added',
               datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
    redis.hset(torrent_key, 'downloaded', 0)
    
    if torrent_file_path:
        if not os.path.isdir(current_app.instance_path):
            os.mkdir(current_app.instance_path)
        new_torrent_file_path = os.path.join(current_app.instance_path,
                                             info_hash + '.torrent')
        shutil.copy(torrent_file_path, new_torrent_file_path)
    
    return True

def _del_torrent(info_hash):
    if not _exist_torrent(info_hash):
        return False    
    torrent_key = 'torrent:%s' % info_hash
    seed_set_key = 'torrent:%s:seed' % info_hash
    leech_set_key = 'torrent:%s:leech' % info_hash
    redis.srem('torrents', info_hash)
    redis.delete(torrent_key)
    redis.delete(seed_set_key)
    redis.delete(leech_set_key)
    
    torrent_file_path = os.path.join(current_app.instance_path,
                                     info_hash + '.torrent')
    if os.path.isfile(torrent_file_path):
        os.path.remove(torrent_file_path)

    return True

def _read_torrent_file(torrent_file_path):
    with open(torrent_file_path, 'rb') as f:
        info_dict = bdecode(f.read())['info']
        info_hash = sha1(bencode(info_dict)).hexdigest()
    return info_hash, info_dict

manager = Manager(app)
manager.add_command("shell", Shell(make_context=_make_context))
manager.add_command("runserver", Server())

@manager.option('-n', '--name', help='Torrent name')
@manager.option('-i', '--info-hash', help='Info hash of torrent')
@manager.option('-f', '--file', help='Torrent file', dest='torrent_file_path')
def add_torrent(name, info_hash, torrent_file_path):
    if torrent_file_path:
        torrent_file_path = os.path.join(os.getcwd(), torrent_file_path)
        if not os.path.isfile(torrent_file_path):
            print "The file %s does not exist." % torrent_file_path
            return
        info_hash, info_dict = _read_torrent_file(torrent_file_path)
        name = info_dict['name']
        if _add_torrent(name, info_hash, torrent_file_path):            
            print "Torrent (%s - %s) added" % (name, info_hash)
        else:
            print "Torrent (%s - %s) already added" % (name, info_hash)
    else:
        if name is None:
            print "Missing torrent name (-n)"
            return
        elif info_hash is None:
            print "Missing info_hash of torrent (-i)"
        elif len(info_hash) != 40:
            print "info_hash must be 40 characters long"
        else:
            if not _add_torrent(name, info_hash):
                print "Torrent (%s - %s) added" % (name, info_hash)
            else:
                print "Torrent (%s - %s) already added"

@manager.option('-i', '--info-hash', help='Info hash of torrent')
@manager.option('-f', '--file', help='Torrent file', dest='torrent_file_path')
def remove_torrent(info_hash, torrent_file_path):
    if torrent_file_path:
        torrent_file_path = os.path.join(os.getcwd(), torrent_file_path)
        if not os.path.isfile(torrent_file_path):
            print "The file %s does not exist." % torrent_file_path
            return
        info_hash, info_dict = _read_torrent_file(torrent_file_path)
        name = info_dict['name']
        if _del_torrent(info_hash):
            print "Torrent (%s - %s) removed" % (name, info_hash) 
        else:
            print "Torrent (%s - %s) already removed" % (name, info_hash)
    else:
        if info_hash is None:
            print "Missing info_hash of torrent (-i)"
        elif len(info_hash) != 40:
            print "info_hash must be 40 characters long"
        else:
            if _del_torrent(info_hash):
                print "Torrent (%s - %s) removed" % (name, info_hash) 
            else:
                print "Torrent (%s - %s) already removed" % (name, info_hash)
                

if __name__ == '__main__':
    manager.run()