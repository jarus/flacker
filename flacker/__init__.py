# -*- coding: utf-8 -*-
"""
    flacker
    ~~~~~~~

    A BitTorrent tracker written in Python with Flask.

    :copyright: 2012 by Christoph Heer <Christoph.Heer@googlemail.com
    :license: BSD, see LICENSE for more details.
"""

import cgi
from binascii import b2a_hex
from socket import inet_aton
from struct import pack

from flask import Flask, request
from flask.ext.redis import Redis

from bencode import bencode

def get_info_hash(request, multiple=False):
    if not multiple:
        return b2a_hex(cgi.parse_qs(request.query_string)['info_hash'][0])
    else:
        hashes = set()
        for hash in cgi.parse_qs(request.query_string)['info_hash']:
            hashes.add(b2a_hex(hash))
        return hashes

def babort(message):
    return bencode({'failure reason': message})

app = Flask("flacker")
redis = Redis(app)

@app.route('/')
def index():
    return ""

@app.route('/announce')
def announce():
    need_args = ('info_hash', 'peer_id', 'port', 'uploaded', 'downloaded', 
                 'left')
    for arg in need_args:
        if arg not in request.args:
            return babort('missing argument (%s)' % arg)

    peer_id = request.args['peer_id']
    peer_key = 'peer:%s' % peer_id
    info_hash = get_info_hash(request)
    torrent_key = 'torrent:%s' % info_hash
    seed_set_key = 'torrent:%s:seed' % info_hash
    leech_set_key = 'torrent:%s:leech' % info_hash
    
    if not redis.sismember('torrents', info_hash):
        return babort('torrent not allowed')
    
    if request.args.get('event') == 'stopped':
        redis.srem(seed_set_key, peer_id)
        redis.srem(leech_set_key, peer_id)
        redis.delete(peer_key)
        return bencode({})
    elif request.args.get('event') == 'completed':
        redis.hincrby(torrent_key, 'downloaded', 1)
    
    redis.hset(peer_key, 'ip', request.args.get('ip', request.remote_addr))
    redis.hset(peer_key, 'port', request.args.get('port', int))
    redis.hset(peer_key, 'uploaded', request.args['uploaded'])
    redis.hset(peer_key, 'downloaded', request.args['downloaded'])
    redis.hset(peer_key, 'left', request.args['left'])
    redis.expire(peer_key, 20)
    
    if request.args.get('left', 1, int) == 0 \
    or request.args.get('event') == 'completed':
        redis.sadd(seed_set_key, peer_id)
        redis.srem(leech_set_key, peer_id)
    else:
        redis.sadd(leech_set_key, peer_id)
        redis.srem(seed_set_key, peer_id)
    
    peer_count = 0
    if request.args.get('compact', False, bool):
        peers = ""
    else:
        peers = []
    for peer_id in redis.sunion(seed_set_key, leech_set_key):
        peer_key = 'peer:%s' % peer_id
        ip, port, left = redis.hmget(peer_key, 'ip', 'port', 'left')
        if (ip and port) is None:
            redis.srem(seed_set_key, peer_key)
            redis.srem(leech_set_key, peer_key)
            continue
        elif peer_count >= request.args.get('numwant', 50, int):
            continue
        elif int(left) == 0 and request.args.get('left', 1, int) == 0:
            continue

        peer_count += 1
        if request.args.get('compact', False, bool):
            ip = inet_aton(ip)
            port = pack(">H", int(port))
            peers += (ip + port)
        else:
            peer = {'ip': ip, 'port': int(port)}
            if 'no_peer_id' not in request.args:
                peer['peer_id'] = peer_id
            peers.append(peer)
    
    return bencode({
        'interval': 20,
        'complete': redis.scard(seed_set_key),
        'incomplete': redis.scard(leech_set_key),
        'peers': peers
    })

@app.route('/scrape')
def scape():
    if 'info_hash' in request.args:
        info_hash_list = get_info_hash(request, multiple=True)
        for info_hash in info_hash_list:
            if not redis.sismember('torrents', info_hash):
                info_hash_list.remove(info_hash)
    else:
        info_hash_list = redis.smembers('torrents')
    
    files = {}
    for info_hash in info_hash_list:
        torrent_key = 'torrent:%s' % info_hash
        seed_set_key = 'torrent:%s:seed' % info_hash
        leech_set_key = 'torrent:%s:leech' % info_hash
        
        name, downloaded = redis.hmget(torrent_key, 'name', 'downloaded')
        files[info_hash] = {
            'name': name,
            'downloaded': downloaded or 0,
            'complete': redis.scard(seed_set_key) or 0,
            'incomplete': redis.scard(leech_set_key) or 0,
        }
        
    return bencode({'files': files})
