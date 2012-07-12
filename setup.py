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
        'flask==0.9',
        'flask-script',
    ]
)