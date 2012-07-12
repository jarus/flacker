# -*- coding: utf-8 -*-
# flacker
# Copyright: (c) 2012 Christoph Heer
# License: BSD


from setuptools import setup

setup(
    name='flacker',
    version='0.2',
    url='https://github.com/jarus/flacker',
    license='BSD',
    author='Christoph Heer',
    author_email='Christoph.Heer@googlemail.com',
    description='BitTorrent tracker written with Python and Flask',
    packages=['flacker'],
    zip_safe=False,
    install_requires=[
        'Flask==0.9',
        'Flask-Script==0.3.3',
        'Flask-And-Redis==0.3.1',
        'BitTorrent-bencode==5.0.8.1',
    ]
)