# -*- coding: utf-8 -*-
"""
    flacker.wsgi
    ~~~~~~~~~~~~

    A BitTorrent tracker written in Python with Flask.

    :copyright: 2012 by Christoph Heer <Christoph.Heer@googlemail.com
    :license: BSD, see LICENSE for more details.
"""

from . import create_app
app = create_app()
