'''
Created on 2015. 11. 10.

@author: biscuit
'''
import queue
import time
import threading
from scipy.sparse import dok_matrix
from algo.low_rank import MatrixCompletion
import numpy as np
import sqlite3 as sql
import algo.color

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
cur = None

'''
def add_preference_row(customer_id):
    global cur
    cur.execute("insert into diver_pref(customer_id) values(?)", (customer_id,))
    #-->other columns have default value 0
'''

#update_preference
#items : list of item_id
#rating : -2~2
def update_preference(customer_id, item_id, new_rating, prev_rating=0):
    global cur
    rating = new_rating - prev_rating
    cur.execute("select type from diver_item where id=?", (item_id,))
    type_, =cur.fetchone()
    # top
    if type_ == 0:
        # pattern, neck, sleeve_level
        cur.execute("select pattern, neck, sleeve_level \
                    from diver_item where id=?", (item_id,))
        p, n, s = cur.fetchone()
        cur.execute("select pattern_%d, neck_%d, sleeveT_%d from diver_pref \
                    where customer_id=?" % (p, n, s),(customer_id,))
        o_p, o_n, o_s = cur.fetchone()
        cur.execute("update diver_pref set pattern_%d=?, neck_%d=?,\
                    sleeveT_%d=? where customer_id=?" % (p, n, s),
                (o_p + rating, o_n + rating, o_s + rating, customer_id))
            
    # outer
    elif type_ == 1:
        # zipper, button, hat, length
        cur.execute("select zipper, button, hat, length_level from diver_item where id=?", (item_id,))
        z, b, h, l = cur.fetchone()
        cur.execute("select zipperO_%d, outer_button_%d, hatO_%d, out_len_%d \
                    from diver_pref where customer_id=?"%(z,b,h,l), (customer_id,))
        o_z, o_b, o_h, o_l = cur.fetchone()
        cur.execute("update diver_pref set zipperO_%d=?, outer_button_%d=?, \
                    hatO_%d=?, out_len_%d=? where customer_id=?"%(z,b,h,l),
                    (o_z+rating, o_b+rating, o_h+rating, o_l+rating, customer_id))
    # bottom
    elif type_ == 2:
        # fit
        cur.execute("select fit from diver_item where id=?", (item_id,))
        f, = cur.fetchone()
        
        cur.execute("select fit_%d from diver_pref where customer_id=?"%f,
                (customer_id,))
        o_f, = cur.fetchone()
        cur.execute("update diver_pref set fit_%d=? where customer_id=?"%f,
                (o_f+rating, customer_id))


def _cal_subscore(item_id, customer_id):
    global conn, cur

    cur.execute("select type from diver_item where id=?", (item_id,))
    type_, = cur.fetchone()

    #top
    if type_ == 0:
        cur.execute("select pattern, neck, sleeve_level \
                    from diver_item where id=?", (item_id,))
        p, n, s = cur.fetchone()

        cur.execute("select pattern_%d, neck_%d, sleeveT_%d from diver_pref where customer_id=?"%(p, n, s),(customer_id,))

        o_p, o_n, o_s = cur.fetchone()

        return 1.2**o_p + 1.2**o_n + 1.2**o_s

    #outer
    elif type_ == 1:
        # zipper, button, hat, length
        cur.execute("select zipper, button, hat, length_level from diver_item where id=?", (item_id,))
        z, b, h, l = cur.fetchone()
        cur.execute("select zipperO_%d, outer_button_%d, hatO_%d, out_len_%d \
                    from diver_pref where customer_id=?" % (z,b,h,l), (customer_id,))
        o_z, o_b, o_h, o_l = cur.fetchone()

        return 1.2**o_z + 1.2**o_b + 1.2**o_h + 1.2**o_l

    #bottom
    elif type_ == 2:
        # color, fit
        cur.execute("select fit from diver_item where id=?", (item_id,))
        f, = cur.fetchone()
            
        cur.execute("select fit_%d from diver_pref where customer_id=?"%f, (customer_id,))
        o_f, = cur.fetchone()

        return  1.2**o_f

    else: 
        return 0

def _handle_q():
    global Q, RATING, USER_NUM, ITEM_NUM
    while True:
        req = Q.get()
        if req is None:
            break
        with r_mutex:
            if 'r' in req[0]:
                u_idx, i_idx, rating = req[1:]
                RATING[(u_idx,i_idx)] = rating
            else:           # "u" or "i" in req[0]
                ty, res = req[0]
                if ty == 'u':
                    for i in range(ITEM_NUM):
                        RATING[(-1,i)] = 0
                    USER_NUM += [-1, 1][res=="+"]
                    RATING.resize((USER_NUM, ITEM_NUM))
                    for i in range(ITEM_NUM):
                        RATING[(-1,i)] = 1
                else:
                    ITEM_NUM += [-1, 1][res=="+"]
                    RATING[(-1,-1)] = 1
                
        Q.task_done()


def _rating_refresh():
    global COMP_RATING, ch_count, LRMC
    with r_mutex:
        LRMC.complete_it("sASD")
    with cr_write:
        COMP_RATING = LRMC.get_optimized_matrix()
    while True:
        time.sleep(SLEEP_TIME)
        with ch_lock:
            if ch_count < FLUSH_MIN:
                continue
            ch_count = 0
        with r_mutex:
            LRMC.complete_it("sASD")
        with cr_write:
            COMP_RATING = LRMC.get_optimized_matrix()

def _score_item(hanger, user_id, item_id, weight):
    global cr_read, cr_write, cur, COMP_RATING

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
            
    
    if len(hanger) != 0:
        points = color.hanger_getColor(hanger)
    
    color_list = color.get_color_list(item_id)
    color_score = {}
    for sty in color_list:
        cids, c_ratios = color._get_color(sty)
        color_d = 0
        for cid, ratio in zip(cids, c_ratios):
            color_d += color.eval_color(points, cid) * ratio / 100
        color_score[sty] = color_d
            
    if len(hanger) != 0:
        max_sty = max(color_d, key=color_d.get)
        score += weight[1]* color_score[max_sty]
    else:
        score += weight[1]

    cur.execute("SELECT rate_count FROM diver_item WHERE id=?",(item_id,))
    rate_count = cur.fetchone()[0]

    if rate_count > LIKE_MAX:
        rate_count = LIKE_MAX

    score += weight[2]* rate_count / LIKE_MAX

    return score, max_sty

''' helper functions '''

def init_rating(cursor_):
    global cur, RATING, USER_NUM, ITEM_NUM, LRMC
    cur = cursor_
    for r in cur.execute("SELECT id FROM diver_customer ORDER BY id"):
        USERS.append(r[0])
    for r in cur.execute("SELECT id FROM diver_item ORDER BY id"):
        ITEMS.append(r[0])
    USER_NUM = len(USERS)
    ITEM_NUM = len(ITEMS)
    RATING = dok_matrix((USER_NUM+1, ITEM_NUM), dtype=np.float)
    for u_id, i_id, rating in cur.execute("SELECT customer_id, item_id, rating FROM diver_rating"):
        RATING[(USERS.index(u_id),ITEMS.index(i_id))] = rating
    for i in range(ITEM_NUM):
        RATING[(-1,i)] = 1
    LRMC = MatrixCompletion(RATING)

    th_q = threading.Thread(None, _handle_q, "q_handle")
    th_r = threading.Thread(None, _rating_refresh, "rate_refresh")

    th_q.start()
    th_r.start()

def rating_fill(user_id, item_id, rating):
    global ch_count
    Q.put(('r', USERS.index(user_id), ITEMS.index(item_id), rating))
    with ch_lock:
        ch_count += 1

def rating_add_user(user_id):
    Q.put(('u+', user_id))

'''
def rating_remove_user(user_id):
    global ch_count
    Q.put(('u-', user_id))
    with ch_lock:
        ch_count += 1
'''
def rating_add_item(item_id):
    Q.put(('i+', item_id))
'''
def rating_remove_item(item_id):
    Q.put(('i-', item_id))
'''
def reorder_items(items, user_id, hanger):
    weight = DEFALUT_WEIGHT
    score_dict = {}
    sub_scores = {}
    sub_min, sub_max = (-1, -1)
    sty_dict = {}
    for i in items:
        sc, max_sty = _score_item(hanger, user_id, i, weight)
        sb_sc = _cal_subscore(i, user_id)
        if (sub_min == -1) or (sub_min > sb_sc):
            sub_min = sb_sc
        if (sub_max == -1) or (sub_max < sb_sc):
            sub_max = sb_sc
        score_dict[i]= sc
        sub_scores[i]= sb_sc
        sty_dict[i] = max_sty    
    
    return sorted(items, key= lambda x: score_dict[x]+ weight[3]*((sub_scores[x]-sub_min) / (sub_max-sub_min))
                  ,reverse = True), sty_dict


def main():
    global RATING, LRMC
    
    conn = sql.connect("../diver/db.sqlite3")
    cur = conn.cursor()
    init_rating(cur)
    color.init_color(cur)
    '''
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
    '''
    
if __name__ == '__main__':
    main()
