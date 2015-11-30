'''
Created on 2015. 11. 10.

@author: biscuit
'''
import time
import threading
from scipy.sparse import dok_matrix
from algo.low_rank import MatrixCompletion
import numpy as np
import sqlite3 as sql
from algo import get_cursor, get_mc
from algo.color import get_color, get_color_list, hanger_getColor, eval_color, init_color
from algo.memcachemutex import MemcacheMutex

DEFALUT_WEIGHT = (60, 20, 20)
FLUSH_MIN = 5
SLEEP_TIME = 5
LIKE_MAX = 50

#update_preference
#items : list of item_id
#rating : -2~2
def update_preference(customer_id, item_id, new_rating, prev_rating=0):
    cur = get_cursor()
    rating = new_rating - prev_rating
    cur.execute("SELECT type FROM diver_item WHERE id=?", (item_id,))
    type_, = cur.fetchone()
    # top
    if type_ == 0:
        # pattern, neck, sleeve_level
        cur.execute("SELECT pattern, neck, sleeve_level \
                    FROM diver_item WHERE id=?", (item_id,))
        p, n, s = cur.fetchone()
        cur.execute("SLELCT pattern_%d, neck_%d, sleeveT_%d FROM diver_pref \
                    WHERE customer_id=?" % (p, n, s),(customer_id,))
        o_p, o_n, o_s = cur.fetchone()
        cur.execute("UPDATE diver_pref SET pattern_%d=?, neck_%d=?,\
                    sleeveT_%d=? WHERE customer_id=?" % (p, n, s),
                (o_p + rating, o_n + rating, o_s + rating, customer_id))
            
    # outer
    elif type_ == 1:
        # zipper, button, hat, length
        cur.execute("SELECT zipper, button, hat, length_level FROM diver_item WHERE id=?", (item_id,))
        z, b, h, l = cur.fetchone()
        cur.execute("SELECT zipperO_%d, outer_button_%d, hatO_%d, out_len_%d \
                    FROM diver_pref WHERE customer_id=?"%(z,b,h,l), (customer_id,))
        o_z, o_b, o_h, o_l = cur.fetchone()
        cur.execute("UPDATE diver_pref SET zipperO_%d=?, outer_button_%d=?, \
                    hatO_%d=?, out_len_%d=? WHERE customer_id=?"%(z,b,h,l),
                    (o_z+rating, o_b+rating, o_h+rating, o_l+rating, customer_id))
    # bottom
    elif type_ == 2:
        # fit
        cur.execute("SELECT fit FROM diver_item WHERE id=?", (item_id,))
        f, = cur.fetchone()
        
        cur.execute("SELECT fit_%d FROM diver_pref WHERE customer_id=?"%f,
                (customer_id,))
        o_f, = cur.fetchone()
        cur.execute("UPDATE diver_pref SET fit_%d=? WHERE customer_id=?"%f,
                (o_f+rating, customer_id))


def _cal_subscore(item_id, customer_id):
    cur = get_cursor()
    cur.execute("SELECT type FROM diver_item WHERE id=?", (item_id,))
    type_, = cur.fetchone()

    #top
    if type_ == 0:
        cur.execute("SELECT pattern, neck, sleeve_level \
                    FROM diver_item WHERE id=?", (item_id,))
        p, n, s = cur.fetchone()

        cur.execute("SELECT pattern_%d, neck_%d, sleeveT_%d FROM diver_pref WHERE customer_id=?"%(p, n, s)
                    ,(customer_id,))

        o_p, o_n, o_s = cur.fetchone()

        return 1.2**o_p + 1.2**o_n + 1.2**o_s

    #outer
    elif type_ == 1:
        # zipper, button, hat, length
        cur.execute("SELECT zipper, button, hat, length_level FROM diver_item WHERE id=?", (item_id,))
        z, b, h, l = cur.fetchone()
        cur.execute("SELECT zipperO_%d, outer_button_%d, hatO_%d, out_len_%d \
                    FROM diver_pref WHERE customer_id=?" % (z,b,h,l), (customer_id,))
        o_z, o_b, o_h, o_l = cur.fetchone()

        return 1.2**o_z + 1.2**o_b + 1.2**o_h + 1.2**o_l

    #bottom
    elif type_ == 2:
        # color, fit
        cur.execute("SELECT fit FROM diver_item WHERE id=?", (item_id,))
        f, = cur.fetchone()
            
        cur.execute("SELECT fit_%d FROM diver_pref WHERE customer_id=?"%f, (customer_id,))
        o_f, = cur.fetchone()

        return  1.2**o_f

    else: 
        return 0

def _rating_refresh():
    mc = get_mc()
    LRMC = mc.get("LRMC")
    ch_count = mc.get("ch_count")
    r_mutex = MemcacheMutex("r_mutex", mc)
    cr_write = MemcacheMutex("cr_write", mc)
    ch_lock = MemcacheMutex("ch_lock", mc)
    with r_mutex:
        LRMC.complete_it("sASD")
        mc.set("LRMC", LRMC, 0)
    with cr_write:
        COMP_RATING = LRMC.get_optimized_matrix()
        mc.set("COMP_RATING", COMP_RATING)
    while True:
        time.sleep(SLEEP_TIME)
        with ch_lock:
            if ch_count < FLUSH_MIN:
                continue
            ch_count = 0
        with r_mutex:
            LRMC.complete_it("sASD")
            mc.set("LRMC", LRMC, 0)
        with cr_write:
            COMP_RATING = LRMC.get_optimized_matrix()
            mc.set("COMP_RATING", COMP_RATING)

def _score_item(hanger, user_id, item_id, weight):
    mc = get_mc()
    USERS = mc.get("USERS")
    ITEMS = mc.get("ITEMS")
    u_idx = USERS.index(user_id)
    i_idx = ITEMS.index(item_id)

    cur = get_cursor()
    mc = get_mc()
    cr_read = mc.get("cr_read")
    cr_mutex = MemcacheMutex("cr_mutex", mc)
    cr_write = MemcacheMutex("cr_write", mc)
    with cr_mutex:
        cr_read += 1
        if cr_read == 1:
            cr_write.acquire()
    COMP_RATING = mc.get("COMP_RATING")
    score = weight[0]* COMP_RATING[u_idx][i_idx]
    with cr_mutex:
        cr_read -= 1
        if cr_read == 0:
            cr_write.release()
            
    points = []
    if len(hanger) != 0:
        points = hanger_getColor(hanger)
        color_list = get_color_list(item_id)
        color_score = {}
        for sty in color_list:
            cids, c_ratios = get_color(sty)
            color_d = 0
            for cid, ratio in zip(cids, c_ratios):
                color_d += eval_color(points, cid) * ratio / 100
            color_score[sty] = color_d
        max_sty = max(color_score, key=color_score.get)
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

def init_rating():
    cur = get_cursor()
    mc = get_mc()
    custs = list(cur.execute("SELECT id FROM diver_customer ORDER BY id"))
    USERS = [-1]
    for r in custs:
        USERS.append(r[0])
    mc.set("USERS", USERS)
    its = list(cur.execute("SELECT id FROM diver_item ORDER BY id"))
    ITEMS = []
    for r in its:
        ITEMS.append(r[0])
    mc.set("ITEMS", ITEMS)
    mc.set("RATING", dok_matrix((len(USERS), len(ITEMS)), dtype=np.float), 0)
    rats = list(cur.execute("SELECT customer_id, item_id, rating FROM diver_rating"))
    RATING = mc.get("RATING")
    for u_id, i_id, rating in rats:
        RATING[(USERS.index(u_id),ITEMS.index(i_id))] = rating
    for i in range(len(ITEMS)):
        RATING[(0,i)] = 1
    mc.set("RATING", RATING, 0)
    mc.set("LRMC", MatrixCompletion(RATING), 0)
    mc.set("ch_count", 0, 0)
    mc.set("cr_read", 0, 0)
    mc.set("COMP_RATING", None, 0)

    th_r = threading.Thread(None, _rating_refresh, "rate_refresh")
    th_r.start()

def rating_fill(user_id, item_id, rating):
    mc = get_mc()
    ch_lock = MemcacheMutex("ch_lock")
    USERS = mc.get("USERS")
    ITEMS = mc.get("ITEMS")
    r_mutex = MemcacheMutex("r_mutex", mc)
    
    u_idx, i_idx = USERS.index(user_id), ITEMS.index(item_id)
    with r_mutex:
        RATING = mc.get("RATING")
        RATING[(u_idx,i_idx)] = rating
        mc.set("RATING", RATING)
    with ch_lock:
        ch_count = mc.get("ch_count")
        ch_count += 1
        mc.set("ch_count", ch_count)

def rating_add_user(user_id):
    # Q.put(('u+', user_id))
    mc = get_mc()
    r_mutex = MemcacheMutex("r_mutex", mc)
    ITEMS = mc.get("ITEMS")
    with r_mutex:
        USERS = mc.get("USERS")
        RATING = mc.get("RATING")
        USERS.append(user_id)
        RATING.resize((len(USERS), len(ITEMS)))
        mc.set("USERS", USERS)
        mc.set("RATING", RATING)

def rating_remove_user(user_id):
    mc = get_mc()
    r_mutex = MemcacheMutex("r_mutex", mc)
    ch_lock = MemcacheMutex("ch_lock", mc)
    ITEMS = mc.get("ITEMS")
    with r_mutex:
        USERS = mc.get("USERS")
        RATING = mc.get("RATING")
        USERS.remove(user_id)
        RATING.resize((len(USERS), len(ITEMS)))
        mc.set("USERS", USERS)
        mc.set("RATING", RATING)
    with ch_lock:
        ch_count = mc.get("ch_count")
        ch_count += 1
        mc.set("ch_count")
        

def rating_add_item(item_id):
    # Q.put(('i+', item_id))
    mc = get_mc()
    r_mutex = MemcacheMutex("r_mutex", mc)
    USERS = mc.get("USERS")
    with r_mutex:
        ITEMS = mc.get("ITEMS")
        RATING = mc.get("RATING")
        ITEMS.append(item_id)
        RATING[(0,-1)] = 1
        RATING.resize((len(USERS), len(ITEMS)))
        mc.set("ITEMS", ITEMS)
        mc.set("RATING", RATING)


def rating_remove_item(item_id):
    #Q.put(('i-', item_id))
    mc = get_mc()
    r_mutex = MemcacheMutex("r_mutex", mc)
    USERS = mc.get("USERS")
    with r_mutex:
        ITEMS = mc.get("ITEMS")
        RATING = mc.get("RATING")
        ITEMS.remove(item_id)
        RATING.resize((len(USERS), len(ITEMS)))
        mc.set("ITEMS", ITEMS)
        mc.set("RATING", RATING)
    
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
    
    conn = sql.connect("../diver/db.sqlite3")
    cur = conn.cursor()
    init_rating(cur)
    init_color(cur)
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
