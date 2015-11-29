'''
Created on 2015. 11. 19.

@author: biscuit
'''

import memcache
from django.db import connection

def get_cursor():
    return connection.cursor()

def get_mc():
    return memcache.Client(["127.0.0.1:20404"])
