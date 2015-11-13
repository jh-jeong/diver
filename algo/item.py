'''
Created on 2015. 11. 10.

@author: biscuit
'''
import queue
import time
import threading
from scipy.sparse import dok_matrix
import numpy as np
from .low_rank import MatrixCompletion

DEFALUT_WEIGHT = (100,)
FLUSH_MIN = 5
SLEEP_TIME = 5

USER_NUM, ITEM_NUM = 0, 0
USERS = []
ITEMS = []

RATING = None
COMP_RATING = None

r_mutex = threading.Lock() 
cr_mutex = threading.Lock()
cr_write = threading.Lock()
ch_lock = threading.Lock()

cr_read = 0
ch_count = 0

Q = queue.Queue()

def _init_rating():
    pass

def score_item(weight, user_id, item_id):
    u_idx = USERS.index(user_id) 
    i_idx = ITEMS.index(item_id)
    with cr_mutex:
        cr_read += 1
        if cr_read == 1:
            cr_write.acquire()
    score = weight * COMP_RATING[u_idx][i_idx]
    with cr_mutex:
        cr_read -= 1
        if cr_read == 0:
            cr_write.release()
    return score

def handle_q():
    while True:
        req = Q.get()
        if req is None:
            break
        with r_mutex:
            if 'r' in req[0]:
                u_id, i_id, rating = req[1:]
                RATING[u_id][i_id] = rating
            else:           # "u" or "i" in req[0]
                ty, res = req[0]
                if ty == 'u':
                    USER_NUM += [-1, 1][res=="+"]
                else:
                    ITEM_NUM += [-1, 1][res=="+"]
                RATING.resize((USER_NUM, ITEM_NUM))
        Q.task_done()


def _rating_refresh():
    while True:
        time.sleep(SLEEP_TIME)
        with ch_lock:
            if ch_count < FLUSH_MIN:
                continue
            ch_count = 0
        with r_mutex:
            result = MatrixCompletion(RATING).get_optimized_matrix()
        with cr_write:
            COMP_RATING = result

def rating_fill(user_id, item_id, rating):
    Q.put(('r', user_id, item_id, rating))
    with ch_lock:
        ch_count += 1

def rating_add_user(user_id):
    Q.put(('u+', user_id))

def rating_remove_user(user_id):
    Q.put(('u-', user_id))
    with ch_lock:
        ch_count += 1

def rating_add_item(item_id):
    Q.put(('i+', item_id))

def rating_remove_item(item_id):
    Q.put(('i-', item_id))
