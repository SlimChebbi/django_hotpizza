from setuptools import setup

import os

# Put here required packages


setup(name='mysite3',
      version='1.0',
      description='Order Pizza Online',
      author='Slim Chebbi',
      author_email='slimchebbiisi@gmail.com',
      url='https://pypi.python.org/pypi',
      install_requires=['Django<=1.6', 'psycopg2<=2.5.3',
                        'Pillow', 'django-redis-cache', 'hiredis', 'South'],
      )
