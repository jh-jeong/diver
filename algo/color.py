'''
Created on 2015. 11. 19.

@author: biscuit
'''
import sqlite3 as sql
from algo.fp import find_frequent_itemsets

cur = None

COLOR = []
COLOR_THRESHOLD = 0.7
COLOR_DMAX = 765

cItemSet= None

PALETTE = {'beige': (245,245,220), 'black': (0,0,0), 'blue': (0,0,255), 'brown': (165,42,42),
           'darkgreen': (0,100,0), 'gold': (255,215,0), 'green':(50,205,50), 'gray':(190,190,190), 
           'ivory': (255,255,240), 'kakhi': (189,183,107), 'mint': (173,255,47), 'navy':(0,0,128), 
           'orange': (255,165,0), 'pink': (255,105,180), 'red': (255,0,0), 'skyblue': (135,206,250), 
           'white':(255,255,255), 'yellow': (255,255,0)}

def _get_color(item_id):
    global cur
    cur.execute("SELECT color_id1, color_ratio1, color_id2, color_ratio2, color_id3, color_ratio3 \
                FROM diver_item WHERE id=?", (item_id,))
    temp = cur.fetchone()
    cid, c_ratio = temp[::2], temp[1::2]
    return cid, c_ratio

def _get_color_type(item_id):
    cid, c_ratio = _get_color(item_id)
    if c_ratio[0] > COLOR_THRESHOLD:
        vec_c = set([cid[0],])
    elif c_ratio[0] + c_ratio[1] > COLOR_THRESHOLD:
        vec_c = set([cid[0], cid[1]])
    else:
        vec_c = set([cid[0], cid[1], cid[2]])
        
    return vec_c

def _get_color_data(match_id):
    global cur
    ColorSet = []
    for m in cur.execute("SELECT outer1_id, outer2_id, top1_id, \
                            top2_id, bottom_id, shoes_id \
                            FROM diver_match WHERE id=?", (match_id,)):
        vec_m = []
        for i in m:
            if i != None:
                vec_m.append(_get_color_type(i))
        ColorSet.append(vec_m)
    # caching
    return ColorSet

def _init_color_data():
    global cur
    colorSet = []
    vec_c = None
    rows = list(cur.execute("SELECT outer1_id, outer2_id, top1_id, top2_id, bottom_id, shoes_id FROM diver_match"))
    for m in rows:
        vec_c = set([])
        for i in m:
            if i != None and type(i) != str:
                vec_c |= _get_color_type(i)
        colorSet.append(vec_c)
    # caching
    return colorSet

''' Helper '''

def init_color(cursor_):
    global COLOR, cItemSet, cur
    cur = cursor_
    COLOR = _init_color_data()
    cItemSet = list(find_frequent_itemsets(COLOR, 2, True))
    
def hanger_getColor(hanger):
    h_set = set([])
    for c in map(_get_color_type, hanger):
        h_set |= c
    cand = {}
    for match, sup in cItemSet:
        if h_set < set(match):
            cand[frozenset(match)]=sup
    
    result = set([])
    for i in sorted(cand, key=cand.get)[:3]:
        result |= i
    return result

def manhattan_color(cid_1, cid_2):
    color_1, color_2 = PALETTE[cid_1], PALETTE[cid_2]
    distance = 0
    distance += abs(color_1[0] - color_2[0])
    distance += abs(color_1[1] - color_2[1])
    distance += abs(color_1[2] - color_2[2])
    return distance

def eval_color(cid_list, cid):
    min_dist = 1000
    for i in cid_list:
        d = manhattan_color(i, cid)
        if d < min_dist:
            min_dist = d
    return 1 - min_dist/COLOR_DMAX

def find_cid(r,g,b):
    min_d = COLOR_DMAX + 1
    min_cid = -1
    for i, c in enumerate(PALETTE.values()):
        d = abs(c[0]-r) + abs(c[1]-g) + abs(c[2]-b)
        if min_d > d:
            min_cid = i
            min_d = d
    return min_cid

def main():
    conn = sql.connect("../diver/db.sqlite3")
    cur = conn.cursor()
    init_color(cur)
    
    print("MATCH SET:")
    print(COLOR)
    
    print()
    print("Caculated Item sets:")
    print(cItemSet)
    
    
if __name__ == '__main__':
    main()

