# -*- coding: utf-8 -*-
"""
    flacker.frontend
    ~~~~~~~~~~~~~~~~

    A BitTorrent tracker written in Python with Flask.

    :copyright: 2012 by Christoph Heer <Christoph.Heer@googlemail.com
    :license: BSD, see LICENSE for more details.
"""

from flask import Blueprint
from flask import current_app as app

from .redis import redis

frontend = Blueprint("frontend", "flacker.frontend.frontend")
@frontend.route('/')
def index():
    return 'Flacker - A BitTorrent tracker written in Python with Flask'