'''
Created on 2015. 11. 10.

@author: biscuit
'''
import sqlite3 as sql
from algo.apriori import apriori


conn = sql.connect("test.sqlite3")
cur_m = conn.cursor()
cur_i = conn.cursor()

category_top = ["t-shirt", "crew", "knit", "shirt", "hood", "sleeveless"] 
category_outer = [""]
category_bottom = ["jean", "cotton", "jogger", "baggy", "slacks"]
pattern = ["none", "multicolors", "checked", "printed", "striped", 
           "snowflake", "floral", "camoflage", "gradation", "twisted"]
collar = [0, 1, 2, 3]

COLOR_THRESHOLD = 0.7

MATCH = []
COLOR = []

mItemSet, mSupport = None, None
cItemSet, cSupport = None, None

def get_item_type(item_id):
    global cur_i
    cur_i.execute("SELECT type, c_id1, c_id1_ratio, c_id2, c_id2_ratio, c_id3, c_id3_ratio FROM items")
    temp = cur_i.fetchone()
    ty, cid, c_ratio = temp[0], temp[1::2], temp[2::2]
    if ty == 0:
        cur_i.execute("SELECT category, pattern FROM top WHERE item_id=?", item_id)
        cat, pat = cur_i.fetchone()
        vec_i = (0, cat, pat)
    elif ty == 1:
        cur_i.execute("SELECT category, collar FROM outer WHERE item_id=?", item_id)
        cat, col = cur_i.fetchone()
        vec_i = (1, cat, col)
    elif ty == 2:
        cur_i.execute("SELECT category FROM bottom WHERE item_id=?", item_id)
        cat = cur_i.fetchone()
        vec_i = (2, cat)
    else:
        cur_i.execute("SELECT category FROM shoes WHERE item_id=?", item_id)
        cat = cur_i.fetchone()
        vec_i = (3, cat)
    
    if c_ratio[0] > COLOR_THRESHOLD:
        vec_c = (cid[0],)
    elif c_ratio[0] + c_ratio[1] > COLOR_THRESHOLD:
        vec_c = (cid[0], cid[1])
    else:
        vec_c = (cid[0], cid[1], cid[2])
    
    return vec_i, vec_c

def get_match_data():
    global cur_m
    dataSet = []
    colorSet = []
    for m in cur_m.execute("SELECT outer_id1, outer_id2, top_id1, top_id2, bottom_id, shoes_id FROM matches"):
        vec_m = []
        vec_c = set([])
        for i in m:
            if i != None:
                res = get_item_type(i)
                vec_m.append(res[0])
                for j in res[1]:
                    vec_c.add(j)
        dataSet.append(vec_m)
        colorSet.append(vec_c)
    # caching
    return dataSet, colorSet

def init_category():
    global MATCH, COLOR, mItemSet, mSupport, cItemSet, cSupport
    MATCH, COLOR = get_match_data()
    mItemSet, mSupport = apriori(MATCH, 0.7)
    cItemSet, cSupport = apriori(COLOR, 0.7)
    

def filter_match():
    pass

def complete_hanger():
    pass

def category_rate():
    pass


    
    




    



