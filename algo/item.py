'''
Created on 2015. 11. 10.

@author: biscuit
'''
import queue
import time
import threading
from scipy.sparse import dok_matrix
from low_rank import MatrixCompletion
import numpy as np
import sqlite3 as sql
import color

DEFALUT_WEIGHT = (80, 20)
FLUSH_MIN = 5
SLEEP_TIME = 5
LIKE_MAX = 50

USER_NUM, ITEM_NUM = 0, 0
USERS = []
ITEMS = []

RATING = None
COMP_RATING = None
LRMC = None

r_mutex = threading.Lock() 
cr_mutex = threading.Lock()
cr_write = threading.Lock()
ch_lock = threading.Lock()

cr_read = 0
ch_count = 0

Q = queue.Queue()
conn = None
cur = None

def _init_rating():
    global conn, cur, RATING, USER_NUM, ITEM_NUM, LRMC 
    conn = sql.connect("test.sqlite3")
    cur = conn.cursor()
    for r in cur.execute("SELECT user_id FROM users ORDER BY user_id"):
        USERS.append(r[0])
    for r in cur.execute("SELECT item_id FROM items ORDER BY item_id"):
        ITEMS.append(r[0])
    USER_NUM = len(USERS)
    ITEM_NUM = len(ITEMS)
    RATING = dok_matrix((USER_NUM, ITEM_NUM), dtype=np.float)
    for u_id, i_id, rating in cur.execute("SELECT user_id, item_id, rating FROM item_conf"):
        RATING[u_id][i_id] = rating
    LRMC = MatrixCompletion(RATING)

def score_item(hanger, user_id, item_id):
    global cr_read, cr_write, cur
    
    weight = DEFALUT_WEIGHT
    # query for weight
    u_idx = USERS.index(user_id) 
    i_idx = ITEMS.index(item_id)
    with cr_mutex:
        cr_read += 1
        if cr_read == 1:
            cr_write.acquire()
    score = weight[0]* COMP_RATING[u_idx][i_idx]
    with cr_mutex:
        cr_read -= 1
        if cr_read == 0:
            cr_write.release()
    
    cid_list, c_ratio = color.get_color(item_id)
    color_d = 0
    points = color.hanger_getColor(hanger)
    for cid, ratio in zip(cid_list, c_ratio):
        color_d += color.eval_color(points, cid) * ratio
    score += weight[1]* color_d
    
    cur.execute("SELECT rate_count FROM items WHERE item_id=?",(item_id,))
    rate_count = cur.fetchone()
    
    if rate_count > LIKE_MAX:
        rate_count = LIKE_MAX
    
    score += weight[2]* rate_count / LIKE_MAX
    
    return score

def reorder_items(items, user_id, hanger):
    return sorted(items, key= lambda x: score_item(hanger, user_id, x))

def handle_q():
    global Q, RATING, USER_NUM, ITEM_NUM
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
    global COMP_RATING
    while True:
        time.sleep(SLEEP_TIME)
        with ch_lock:
            if ch_count < FLUSH_MIN:
                continue
            ch_count = 0
        with r_mutex:
            LRMC.complete_it("ASD")
        with cr_write:
            COMP_RATING = LRMC.get_optimized_matrix()

def rating_fill(user_id, item_id, rating):
    global ch_count
    Q.put(('r', user_id, item_id, rating))
    with ch_lock:
        ch_count += 1

def rating_add_user(user_id):
    Q.put(('u+', user_id))

def rating_remove_user(user_id):
    global ch_count
    Q.put(('u-', user_id))
    with ch_lock:
        ch_count += 1

def rating_add_item(item_id):
    Q.put(('i+', item_id))

def rating_remove_item(item_id):
    Q.put(('i-', item_id))


def main():
    global RATING, LRMC
    _init_rating()
    color.init_color()
    RATING = RATING.toarray()
    with open("test.csv", "r") as f:
        for i, l in enumerate(f):
            vals = l.split(",")
            for j, v in enumerate(vals):
                try:
                    RATING[i][j] = float(v)
                except ValueError:
                    RATING[i][j] = np.NaN
    LRMC._M = RATING
    print("################################## BEFORE")
    print(LRMC.get_matrix())
    LRMC.complete_it("ASD")
    C = LRMC.get_optimized_matrix()
    for i, rows in enumerate(C):
        for j, elem in enumerate(rows):
            C[i][j] = round(C[i][j])
    print()
    print("################################## AFTER")
    print(C)
        
if __name__ == '__main__':
    main()