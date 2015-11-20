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

DEFALUT_WEIGHT = (60, 20, 20)
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

def add_prefercence_row(user_id):
    global cur
    cur.execute("insert into preference(user_id) values(?)", (user_id,))
    #-->other columns have default value 0


#update_preference
#items : list of item_id
#rating : -2~2
def update_preference(user_id, item_id, new_rating, prev_rating=0):
    global cur
    rating = new_rating - prev_rating
    cur.execute("select type from items where item_id=?", (item_id,))
    type_, =cur.fetchone()
    # top
    if type_ == 0:
        # pattern, color, neck, sleeve_level
        cur.execute("select pattern, neck, sleeve_level \
                    color_id1, color_ratio1, \
                    color_id2, color_ratio2, \
                    color_id3, color_ratio3 from items where \
                    item_id=?", (item_id,))
        t = cur.fetchone()
        p, n, s = t[:3]
        c = t[3:]
        colors = []
        for v in zip(c[0::2], c[1::2]):
            colors.append(v)
        cur.execute("select pattern_%d, neck_%d, sleeveT_%d from preference \
                    where user_id=?" % (p, n, s),(user_id,))
        o_p, o_n, o_s = cur.fetchone()
        cur.execute("update preference set pattern_%d=?, neck_%d=?,\
                    sleeveT_%d=? where user_id=?" % (p, n, s),
                (o_p + rating, o_n + rating, o_s + rating, user_id))
        for c, c_r in colors:
            cur.execute("select top_%d from preference where user_id=?" %c,(user_id,))
            o_c, = cur.fetchone()
            cur.execute("update preference set top_%d=? where user_id=?"%c,(o_c + rating*c_r, user_id))
    # outer
    elif type_ == 1:
        # zipper, button, hat, length
        cur.execute("select zipper, button, hat, length_level from items \
                    where item_id=?", (item_id,))
        z, b, h, l = cur.fetchone()
        cur.execute("select zipperO_%d, outer_button_%d, hatO_%d, out_len_%d \
                    from preference where user_id=?"%(z,b,h,l), (user_id,))
        o_z, o_b, o_h, o_l = cur.fetchone()
        cur.execute("update preference set zipperO_%d=?, outer_button_%d=?, \
                    hatO_%d=?, out_len_%d=? where user_id=?"%(z,b,h,l),
                    (o_z+rating, o_b+rating, o_h+rating, o_l+rating, user_id))
    # bottom
    elif type_ == 2:
        # color, fit
        colors = []
        cur.execute("select fit \
                    color_id1, color_ratio1, \
                    color_id2, color_ratio2, \
                    color_id3, color_ratio3 from items where \
                    item_id=?", (item_id,))
        t = cur.fetchone()
        f = t[0]
        c = t[1:]
        for v in zip(c[0::2], c[1::2]):
            colors.append(v)
        for c, c_r in colors:
            cur.execute("select bottom_%d from preference where user_id=?"%c,
                    (user_id,))
            o_c, = cur.fetchone()
            cur.execute("update preference set bottom_%d=? where user_id=?"%c,
                    (o_c + rating*c_r, user_id))
            
        cur.execute("select fit_%d from preference where user_id=?"%f,
                (user_id,))
        o_f, = cur.fetchone()
        cur.execute("update preference set fit_%d=? where user_id=?"%f,
                (o_f+rating, user_id))


def cal_subscore(item_id, user_id):
    global conn, cur

    cur.execute("select type from items where item_id=?", (item_id,))
    type_, = cur.fetchone()

    #top
    if type_ == 0:
        cur.execute("select pattern, neck, sleeve_level \
                    color_id1, color_ratio1, \
                    color_id2, color_ratio2, \
                    color_id3, color_ratio3 from items where \
                    item_id=?", (item_id,))
        t = cur.fetchone()
        p, n, s = t[:3]
        c = t[3:]
        colors = []
        for v in zip(c[0::2], c[1::2]):
            colors.append(v)

        cur.execute("select pattern_%d, neck_%d, sleeveT_%d from preference \
            where user_id=?"%(p, n, s),(user_id,))

        o_p, o_n, o_s = cur.fetchone()
        sum_ = 0
        for c, c_r in colors:
            cur.execute("select top_%d from preference where user_id=?" %c,(user_id,))
            o_c, = cur.fetchone()
            sum_ += 1.2**(o_c*c_r)

        return 1.2**o_p + 1.2**o_n + 1.2**o_s + sum_

    #outer
    elif type_ == 1:
        # zipper, button, hat, length
        cur.execute("select zipper, button, hat, length_level from items \
                    where item_id=?", (item_id,))
        z, b, h, l = cur.fetchone()
        cur.execute("select zipperO_%d, outer_button_%d, hatO_%d, out_len_%d \
                    from preference where user_id=?" % (z,b,h,l), (user_id,))
        o_z, o_b, o_h, o_l = cur.fetchone()

        return 1.2**o_z + 1.2**o_b + 1.2**o_h + 1.2**o_l

    #bottom
    elif type_ == 2:
        # color, fit
        colors = []
        cur.execute("select fit \
                    color_id1, color_ratio1, \
                    color_id2, color_ratio2, \
                    color_id3, color_ratio3 from items where \
                    item_id=?", (item_id,))
        t = cur.fetchone()
        f = t[0]
        c = t[1:]
        for v in zip(c[0::2], c[1::2]):
            colors.append(v)
            
        sum_ = 0
        for c, c_r in colors:
            cur.execute("select bottom_%d from preference where user_id=?"%c, (user_id,))
            o_c, = cur.fetchone()
            sum_ += 1.2**(o_c*c_r)

        cur.execute("select fit_%d from preference where user_id=?"%f, (user_id,))
        o_f, = cur.fetchone()

        return  1.2**o_f + sum_

    else: 
        return 0


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

    th_q = threading.Thread(None, _handle_q, "q_handle", daemon=True)
    th_r = threading.Thread(None, _rating_refresh, "rate_refresh", daemon=True)

    th_q.start()
    th_r.start()

def _handle_q():
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
    global COMP_RATING, ch_count
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


''' helper functions '''

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
    if len(hanger) != 0:
        points = color.hanger_getColor(hanger)
        for cid, ratio in zip(cid_list, c_ratio):
            color_d += color.eval_color(points, cid) * ratio
        score += weight[1]* color_d
    else:
        score += weight[1]

    cur.execute("SELECT rate_count FROM items WHERE item_id=?",(item_id,))
    rate_count = cur.fetchone()[0]

    if rate_count > LIKE_MAX:
        rate_count = LIKE_MAX

    score += weight[2]* rate_count / LIKE_MAX

    return score

def reorder_items(items, user_id, hanger):
    return sorted(items, key= lambda x: score_item(hanger, user_id, x))


def main():
    global RATING, LRMC
    _init_rating()
    color.init_color()
    with open("test.csv", "r") as f:
        for i, l in enumerate(f):
            vals = l.split(",")
            for j, v in enumerate(vals):
                try:
                    RATING[(i,j)] = float(v)
                except ValueError:
                    pass
    LRMC._M = RATING
    print("################################## BEFORE")
    print(LRMC.get_matrix())
    LRMC.complete_it("sASD")
    C = LRMC.get_optimized_matrix()
    for i, rows in enumerate(C):
        for j, elem in enumerate(rows):
            C[i][j] = round(elem)
    print()
    print("################################## AFTER")
    print(C)
if __name__ == '__main__':
    main()
