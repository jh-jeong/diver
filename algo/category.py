'''
Created on 2015. 11. 10.

@author: biscuit
'''
import sqlite3 as sql
from algo.fp import find_frequent_itemsets
from algo import color
from algo.color import init_color

cur = None

category_top = ["t-shirt", "crew", "knit", "shirt", "hood", "sleeveless"] 
category_outer = ["stadium jumper", "blouson", "jumper", "denim", "jacket", "coat", "vest", "cardigan"]
category_bottom = ["jean", "cotton", "jogger", "baggy", "slacks"]
pattern = ["none", "multicolors", "checked", "printed", "striped", 
           "snowflake", "floral", "camoflage", "gradation", "twisted"]
collar = [0, 1, 2, 3]

MATCH = []
COLOR = []

mItemSet = None

def _get_item_type(item_id):
    global cur
    cur.execute("SELECT type, category, pattern, collar, padding FROM diver_item WHERE id=?", (item_id,))
    temp = cur.fetchone()
    ty = temp[0]
    
    vec_i = [(0, temp[1], temp[2]), 
             (1, temp[1], temp[3], temp[4]), 
             (2, temp[1]), 
             (3, temp[1])][ty]
    return vec_i

def _get_match_data(match_id):
    global cur
    dataSet = []
    mData = list(cur.execute("SELECT outer1_id, outer2_id, top1_id, \
                            top2_id, bottom_id, shoes_id \
                            FROM diver_match WHERE match_id=?", (match_id,)))
    for m in mData:
        vec_m = []
        for i in m:
            if i != None:
                item_id = color._get_item_id(i)
                vec_m.append(_get_item_type(item_id))
        dataSet.append(vec_m)
    # caching
    return dataSet

def _hanger_getMatch(hanger):
    i_hanger = map(color._get_item_id, hanger)
    h_set = set(map(_get_item_type, i_hanger))
    cand = {}
    for match, sup in mItemSet:
        if h_set < set(match):
            cand[frozenset(match)]=sup
    return cand


def init_match_data():
    global cur
    dataSet = []
    mats = list(cur.execute("SELECT outer1_id, outer2_id, top1_id, top2_id, bottom_id, shoes_id FROM diver_match"))
    for m in mats:
        vec_m = []
        for i in m:
            if i != None and type(i) != str:
                item_id = color._get_item_id(i)
                vec_m.append(_get_item_type(item_id))
        dataSet.append(vec_m)
    # caching
    return dataSet

def init_category(cursor_):
    global MATCH, mItemSet, cur
    cur = cursor_
    MATCH = init_match_data()
    mItemSet = list(find_frequent_itemsets(MATCH, 1, True))
    
def hanger_complete(hanger, customer_id):
    global cur
    
    candDict = _hanger_getMatch(hanger)
    ratings = list(cur.execute("SELECT rating, match_id FROM diver_rating WHERE customer_id=?", (customer_id,)))
    for r, mid in ratings:
        s = frozenset(_get_match_data(mid))
        try:
            candDict[s] = candDict[s]*(r+2)/4
        except KeyError:
            pass
    return max(candDict, key=candDict.get)
    
def main():
    global cur
    conn = sql.connect("../diver/db.sqlite3")
    cur = conn.cursor()
    init_color(cur)
    init_category(cur)
    
    print("MATCH SET:")
    print(MATCH)
    
    print()
    print("Caculated Item sets:")
    print(mItemSet)
    
if __name__ == '__main__':
    main()

