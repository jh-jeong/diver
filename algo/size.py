'''
Created on 2015. 11. 10.

@author: biscuit
'''
import collections
import sqlite3 as sql
import numpy as np
from sklearn import linear_model


#body_type = {"A": "thin", "B": "obesity", "T": "long","S": "short", "M": "mascular",
#"O":"abdominal_obesity"}

Size = collections.namedtuple('Size', ['height','weight', 'leg', 'chest',
                                        'waist', 'hip','thigh'])

conn = sql.connect("test.sqlite3")
cur = conn.cursor()


'''
filter the list of items according to existance proper size
for a given user_id
'''


def size_filter_shoes(items, user_id): #item_id�쓽list瑜� 諛쏅뒗�떎?
    return_list = []


def size_filter_bottom(items, leg, waist, hip, thigh):
    filtered_list = []
    for item_id in items:
        temp = cur.execute("SELECT length_level FROM item WHERE item_id=?", (item_id,))
        level = temp.fetchone()[0]
        if level == 4:
            for length_, crotch_, waist_, thigh_, hip_ in \
                cur.execute("SELECT length_cm, crotch_cm, waist_cm,\
                thigh_cm, hip_cm FROM size WHERE item_id=?",(item_id,)):
                if leg < (length_ - crotch_) and waist < waist_ and \
                    hip < hip_ and thigh < thigh_:
                    filtered_list.append(item_id)
                    break
        else:
            for waist_, thigh_, hip_ in cur.execute("SELECT waist_cm, thigh_cm,\
                hip_cm FROM size WHERE item=id?",item_id):
                if waist < waist_ and thigh < thigh_ and hip < hip_:
                    filtered_list.append(item_id)
                    break

    return filtered_list


def size_filter_top(items, chest):
    filtered_list = []
    for item_id in items:
        for chest_, in cur.execute("SELECT chest_cm FROM size WHERE item_id=?", item_id):
            if chest < chest_:
                filtered_list.append(item_id)
                break

    return filtered_list


def size_filter(items, user_id, class_):
    height, weight, body_shape, leg, chest, waist, hip, thigh = \
            cur.execute("SELECT height_cm, weight_kg, body_shape, size_leg, \
            size_chest, size_waist, size_hip, size_thigh FROM users WHERE \
            user_id=%d"%user_id)
    height, weight, body_shape, leg, chest, waist, hip, thigh = \
            complete_size(height, weight, body_shape, leg, chest, waist, hip, thigh)

    if class_ in ['outer', 'top']:
        filtered_list = size_filter_top(items, chest, class_)
    elif class_ == 'bottom':
        filtered_list = size_filter_bottom(items, leg, waist, hip, thigh)
    else:
        filtered_list = items

    return filtered_list

'''
complete size configuration
for given an size configuration vector and user conf,
return the complete size configuration vector
'''


def size2array(size_list):
    return_list = []

    # X
    return_list.append([[size.height, size.weight] for size in size_list])

    # y's
    for i in range(2,7):
        array = [size[i] for size in size_list]
        #array = np.array(array)
        return_list.append(array)

    return tuple(return_list)


def complete_size(height, weight, body_shape, \
        leg_=None, chest_=None, waist_=None, hip_=None, thigh_=None):

    size_list = []
    clf = linear_model.LinearRegression()

    if body_shape == 'O': #蹂듬�鍮꾨쭔�삎
        #size_list.append(Size(160, 58, 67, 88, 78, 89, 42)) #SO
        size_list.append(Size(165, 63, 68, 90, 80, 91, 43)) #MO
        size_list.append(Size(170, 68, 70, 92, 82, 93, 45)) #MLO
        size_list.append(Size(175, 72, 72, 94, 84, 95, 47)) #LO
    elif body_shape == 'M': #洹쇱쑁�삎
        size_list.append(Size(165, 61, 69, 92, 72, 90, 44)) #MM
        size_list.append(Size(170, 65, 71, 94, 74, 92, 46)) #MLM
        size_list.append(Size(175, 69, 73.5, 96, 76, 94, 48)) #LM
    elif body_shape == 'A': #留덈Ⅸ�삎
        size_list.append(Size(165, 58, 69, 88, 70, 89, 42)) #MA
        size_list.append(Size(170, 63, 71, 90, 72, 91, 44)) #MLA
        size_list.append(Size(175, 67, 73.5, 92, 74, 93, 46)) #LA
    elif body_shape == 'B': #鍮꾨쭔�삎
        size_list.append(Size(160, 60, 67, 92, 78, 91, 45)) #SB
        size_list.append(Size(165, 65, 69, 94, 80, 93, 47)) #MB
        size_list.append(Size(170, 70, 71, 94, 80, 94, 49)) #MLB
        size_list.append(Size(175, 75, 73.5, 98, 84, 97, 51)) #LB
        size_list.append(Size(180, 80, 75.5, 100, 86, 98, 53)) #XLB
    else: #蹂댄넻泥댄삎
        size_list.append(Size(160, 56, 67, 88, 72, 89, 42)) #S
        size_list.append(Size(165, 62, 69, 90, 74, 91, 44)) #M
        size_list.append(Size(170, 66, 71, 92, 76, 93, 46)) #ML
        size_list.append(Size(175, 71, 73.5, 94, 78, 95, 48)) #L
        size_list.append(Size(180, 76, 75.5, 96, 80, 96, 50)) #XL

    X, y_leg, y_chest, y_waist, y_hip, y_thigh = \
            size2array(size_list)
    if leg_ == None:
        clf.fit(X, y_leg)
        leg, = clf.predict([[height, weight]])
    else:
        leg = leg_

    if chest_ == None:
        clf.fit(X, y_chest)
        chest, = clf.predict([[height, weight]])
    else:
        chest = chest_

    if waist_ == None:
        clf.fit(X, y_waist)
        waist, = clf.predict([[height, weight]])
    else:
        waist = waist_

    if hip_ == None:
        clf.fit(X, y_hip)
        hip, = clf.predict([[height, weight]])
    else:
        hip = hip_

    if thigh_ == None:
        clf.fit(X, y_thigh)
        thigh, = clf.predict([[height, weight]])
    else:
        thigh = thigh_

    return (height, weight, leg, chest, waist, hip, thigh)

