'''
Created on 2015. 11. 10.

@author: biscuit
'''
import sqlite3 as sql
from fp_growth import find_frequent_itemsets

conn, cur_m, cur_i = None, None, None

category_top = ["t-shirt", "crew", "knit", "shirt", "hood", "sleeveless"] 
category_outer = [""]
category_bottom = ["jean", "cotton", "jogger", "baggy", "slacks"]
pattern = ["none", "multicolors", "checked", "printed", "striped", 
           "snowflake", "floral", "camoflage", "gradation", "twisted"]
collar = [0, 1, 2, 3]

MATCH = []
COLOR = []

mItemSet = None

def _get_item_type(item_id):
    global cur_i
    cur_i.execute("SELECT type FROM items WHERE item_id=?", (item_id,))
    temp = cur_i.fetchone()
    ty = temp[0] 
    if ty == 0:
        cur_i.execute("SELECT category, pattern FROM top WHERE item_id=?", (item_id,))
        cat, pat = cur_i.fetchone()
        vec_i = (0, cat, pat)
    elif ty == 1:
        cur_i.execute("SELECT category, collar FROM outer WHERE item_id=?", (item_id,))
        cat, col = cur_i.fetchone()
        vec_i = (1, cat, col)
    elif ty == 2:
        cur_i.execute("SELECT category FROM bottom WHERE item_id=?", (item_id,))
        cat = cur_i.fetchone()[0]
        vec_i = (2, cat)
    else:
        cur_i.execute("SELECT category FROM shoes WHERE item_id=?", (item_id,))
        cat = cur_i.fetchone()[0]
        vec_i = (3, cat)

    return vec_i

def _get_match_data(match_id):
    global cur_m
    dataSet = []
    for m in cur_m.execute("SELECT outer_id1, outer_id2, top_id1, \
                            top_id2, bottom_id, shoes_id \
                            FROM matches WHERE match_id=?", (match_id,)):
        vec_m = []
        for i in m:
            if i != None:
                vec_m.append(_get_item_type(i))
        dataSet.append(vec_m)
    # caching
    return dataSet

def _hanger_getMatch(hanger):
    h_set = set(map(_get_item_type, hanger))
    cand = {}
    for match, sup in mItemSet:
        if h_set < set(match):
            cand[frozenset(match)]=sup
    return cand


def init_match_data():
    global cur_m
    dataSet = []
    for m in cur_m.execute("SELECT outer_id1, outer_id2, top_id1, top_id2, bottom_id, shoes_id FROM matches"):
        vec_m = []
        for i in m:
            if i != None and type(i) != str:
                vec_m.append(_get_item_type(i))
        dataSet.append(vec_m)
    # caching
    return dataSet

def init_category():
    global MATCH, mItemSet, conn, cur_m, cur_i
    conn = sql.connect("test.sqlite3")
    cur_m = conn.cursor()
    cur_i = conn.cursor()
    MATCH = init_match_data()
    mItemSet = list(find_frequent_itemsets(MATCH, 2, True))
    
def hanger_complete(hanger, user_id):
    global cur_m
    
    candDict = _hanger_getMatch(hanger)
    
    for r, mid in cur_m.execute("SELECT rating, match_id FROM ratings WHERE user_id=?", (user_id,)):
        s = frozenset(_get_match_data(mid))
        try:
            candDict[s] = candDict[s]*r/5
        except KeyError:
            pass
    return max(candDict, key=candDict.get)
    
def main():
    init_category()
    
    print("MATCH SET:")
    print(MATCH)
    
    print()
    print("Caculated Item sets:")
    print(mItemSet)
    
    conn.close()
    
if __name__ == '__main__':
    main()

