# -*- coding: utf-8 -*-
"""
    flacker.frontend
    ~~~~~~~~~~~~~~~~

    A BitTorrent tracker written in Python with Flask.

    :copyright: 2012 by Christoph Heer <Christoph.Heer@googlemail.com
    :license: BSD, see LICENSE for more details.
"""

from flask import Blueprint, render_template, jsonify, url_for

from .tracker import get_torrent_list

frontend = Blueprint("frontend", "flacker.frontend.frontend")
@frontend.route('/')
def index():
    return render_template("index.html", torrents=get_torrent_list())
