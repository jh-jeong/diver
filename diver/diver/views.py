import sys, os
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.http import JsonResponse

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect

from django.shortcuts import render, redirect, render_to_response
from django.core.files import File
from django.core.files import storage

from diver.models import Image
from diver.models import Item
from diver.models import Customer
from diver.models import Match
from diver.models import ItemPref, Color, Size, Pref, Rating
from diver.settings import IMAGE_DIR
from diver.settings import STATIC_ROOT
from diver.settings import BASE_DIR

import json

sys.path.append(os.path.join(BASE_DIR, '..'))
import algo.item as algo_item
import algo.color as algo_color
import algo.size as algo_size
import algo.category as algo_category

__author__ = 'un'


def survey_required(function):
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/auth')
        elif request.session.get('customer_id') is not None:
            return function(request, *args, **kwargs)
        elif Customer.objects.filter(user_id=request.user.id).count() > 0:
            request.session['customer_id'] = Customer.objects.filter(user_id=request.user.id)[0].id
            return function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/account')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def auth(request):
    return render(request, 'auth.html')


def noneCheck(input):
    if input == '':
        return 0
    return input


def account(request):
    if request.method == 'GET':
        customer = None
        if Customer.objects.filter(user=request.user).count() != 0:
            customer = Customer.objects.get(user=request.user)
    elif request.method == 'POST':
        if Customer.objects.filter(user=request.user).count() == 0:
            customer = Customer(user=request.user, height_cm=180, weight_kg=73,
                                chest_size_cm=50, waist_size_cm=30,
                                leg_length_cm=30, shoes_size_mm=270, hip_cm=30, thigh_cm=30)
            customer.save()
        else:
            customer = Customer.objects.get(user=request.user)

        # Initialize personal preference
        pref = Pref()
        pref.customer = customer
        pref.save()
        algo_item.rating_add_user(customer.id)

        height_cm = request.POST['height_cm']
        weight_kg = request.POST['weight_kg']
        chest_size_cm = request.POST['chest_size_cm']
        waist_size_cm = request.POST['waist_size_cm']
        leg_length_cm = request.POST['leg_length_cm']
        shoes_size_mm = request.POST['shoes_size_mm']
        hip_cm = request.POST['hip_cm']
        thigh_cm = request.POST['thigh_cm']

        body_shape = request.POST.get('body_shape', 'O')

        height_cm = float(noneCheck(height_cm))
        weight_kg = float(noneCheck(weight_kg))
        chest_size_cm = float(noneCheck(chest_size_cm))
        waist_size_cm = float(noneCheck(waist_size_cm))
        leg_length_cm = float(noneCheck(leg_length_cm))
        shoes_size_mm = float(noneCheck(shoes_size_mm))
        thigh_cm = float(noneCheck(thigh_cm))
        hip_cm  = float(noneCheck(hip_cm))

        tmp_tuple = algo_size.complete_size(height_cm,weight_kg,body_shape,leg_length_cm,chest_size_cm,waist_size_cm,hip_cm,thigh_cm)

        height_cm= float(tmp_tuple[0])
        weight_kg=float(tmp_tuple[1])
        leg_length_cm= float(tmp_tuple[2])
        chest_size_cm= float(tmp_tuple[3])
        waist_size_cm =float(tmp_tuple[4])
        hip_cm = float(tmp_tuple[5])
        thigh_cm = float(tmp_tuple[6])

        if customer != None:
            customer.user = request.user
            customer.height_cm = height_cm
            customer.weight_kg = weight_kg
            customer.chest_size_cm = chest_size_cm
            customer.waist_size_cm = waist_size_cm
            customer.leg_length_cm = leg_length_cm
            customer.shoes_size_mm = shoes_size_mm
            customer.body_shape = body_shape
            customer.hip_cm = hip_cm
            customer.thigh_cm = thigh_cm
            customer.save()

        else:
            customer = Customer(user=request.user, height_cm=height_cm, weight_kg=weight_kg,
                                chest_size_cm=chest_size_cm, waist_size_cm=waist_size_cm, hip_cm = hip_cm, thigh_cm = thigh_cm,
                                leg_length_cm=leg_length_cm, shoes_size_mm=shoes_size_mm, body_shape=body_shape
            )
            customer.save()
    return render(request, 'account.html', {'customer': customer})


@survey_required
def main(request):
    if request.method == 'GET':
        matches = Match.objects.all()

    pairs = []
    customer_id = Customer.objects.get(user_id=request.user.id)
    for match in matches:
        try:
            score = Rating.objects.get(match=match, customer_id=customer_id).score
        except:
            score = None
        pairs.append((match, score))

    return render(request, 'main.html', {'pairs': pairs})

def item_rerating(item, score, user_id):
    customer = Customer.objects.get(user_id = user_id)
    prev_score = 0
    if ItemPref.objects.filter(item_id=item, customer=customer).count() != 0:
        item_pref = ItemPref.objects.get(item_id=item, customer=customer)
        prev_score = item_pref.score
        item.rate_count -= item_pref.score
        item_pref.score = score
        item.rate_count += item_pref.score
    else:
        item_pref = ItemPref(item_id=item.id, customer=customer, score=score)
        item.rate_count += item_pref.score
    item.save()
    item_pref.save()
    algo_item.rating_fill(customer.id, item.id, score)
    algo_item.update_preference(customer.id, item.id, score, prev_score)

def match_rating(match, score, user_id):
    for color in [match.outer1, match.outer2, match.top1, match.top2, match.bottom]:
        if color is not None:
            item_rerating(color.item, score, user_id)

@survey_required
def like(request, id):
    try:
        score = int(request.POST['score'])
        item = Item.objects.get(id=id)
        item_rerating(item, score, request.user.id)
        return JsonResponse({'result': 'ok'})
    except Exception as e:
        return JsonResponse({'result': 'fail', 'error': str(e)})

@survey_required
def match_like(request, match_id, score):
    # 범위를 -2 ~ 2로 맞추어 줌
    match_id, score = int(match_id), int(score) - 3

    if request.method == 'GET':
        customer = Customer.objects.get(user_id=request.user.id)
        match = Match.objects.get(id=match_id)

        # Rating 없을 시 만들어줌
        if Rating.objects.filter(customer=customer, match=match).count() == 0:
            rating = Rating(customer=customer, match=match, score=score)
            rating.save()
            match.rate_count += score

        # Rating 존재 시 rate_count 업데이트
        else:
            rating = Rating.objects.get(customer=customer, match=match)
            match.rate_count -= rating.score
            rating.score = score
            match.rate_count += score
            match.save()

        # 매치 내의 아이템들에 점수 반영
        match_rating(match, score+3, request.user.id)

    return HttpResponse("매치{}의 점수: {}".format(match_id, score))

def get_match_from_hanger(hanger, customer_id):
    matched_categories = []
    if len(hanger) > 0:
        matches = algo_category.hanger_complete(hanger, customer_id)
        if matches:
            for match in matches:
                matched_category = {"type": match[0],
                                    "text": match[1],
                                    "category_code": Item.get_category_code(match[1])}
                if match[0] == 0:  # Top
                    matched_category["pattern"] = match[2]
                elif match[0] == 1:  # Outer
                    matched_category["collar"] = match[2]
                    matched_category["padding"] = match[3]
                matched_categories.append(matched_category)
    return matched_categories

@survey_required
def search(request):
    selected_category1 = 0
    selected_category2 = Item.CATEGORIES[0][1][0][0]
    pattern = 0
    collar = 0
    padding = 0
    specified_lower = None
    specified_upper = None
    search_result = []
    customer_id = request.session['customer_id']

    if 'category' in request.GET:
        category = request.GET['category']

        for i in range(len(Item.CATEGORIES)):
            for c, n in Item.CATEGORIES[i][1]:
                if c == category:
                    selected_category1 = i
                    selected_category2 = c
                    break

        items = Item.objects.filter(category=category)
        try:
            specified_lower = int(request.GET['lower'])
            items = items.exclude(price__lte=specified_lower)
        except:
            pass
        try:
            specified_upper = int(request.GET['upper'])
            items = items.exclude(price__gte=specified_upper)
        except:
            pass

        if selected_category1 == 0:
            if 'pattern' in request.GET:
                pattern = request.GET['pattern']
                if pattern != "ALL":
                    items = items.filter(pattern=pattern)

        if selected_category1 == 1:
            if 'collar' in request.GET:
                collar = request.GET['collar']
                if collar != "ALL":
                    items = items.filter(collar=collar)
            if 'padding' in request.GET:
                padding = request.GET['padding']
                if padding != "ALL":
                    items = items.filter(padding=padding)

        ordered_item_ids, styles = algo_item.reorder_items(
                [item.id for item in items],
                request.session['customer_id'],
                request.session.get('hanger', []))

        for item_id in ordered_item_ids:
            item = Item.objects.get(id=item_id)
            try:
                score = ItemPref.objects.get(item=item,
                        customer_id=request.session['customer_id']).score
            except:
                score = None
            search_result.append((item, score))

    matched_categories = get_match_from_hanger(
            request.session.get('hanger', []),
            request.session['customer_id'])

    return render(request, 'search.html',
                  {'categories': Item.CATEGORIES,
                   'patterns': Item.PATTERNS,
                   'selected_pattern': pattern,
                   'selected_collar': collar,
                   'selected_padding': padding,
                   'selected_category1': selected_category1,
                   'selected_category2': selected_category2,
                   'lower': specified_lower,
                   'upper': specified_upper,
                   'search_result': search_result,
                   'hanger': request.session.get('hanger', None),
                   'matched_categories': json.dumps(matched_categories)})


def update_hanger(request):
    if request.method == 'POST':
        action = request.POST['action']
        item_id = int(request.POST['item_id'])

        if not request.session.get('hanger', False):
            request.session['hanger'] = []

        if action == 'ADD':
            if item_id in request.session['hanger']:
                return JsonResponse({"result": "duplicate"})
            new_hanger = request.session['hanger']
            new_hanger.append(item_id)
            request.session['hanger'] = new_hanger
        elif action == 'REMOVE':
            if item_id in request.session['hanger']:
                new_hanger = request.session['hanger']
                new_hanger.remove(item_id)
                request.session['hanger'] = new_hanger
            else:
                return JsonResponse({"result": "not exist"});
        else:
            raise SuspiciousMultipartForm()
        matched_categories = get_match_from_hanger(new_hanger, request.session['customer_id'])
        return JsonResponse({"result": "ok", "match": matched_categories})
    else:
        raise SuspiciousMultipartForm()


@survey_required
def upload(request):
    if request.method == 'POST':
        # filename = request.POST["filename"]

        if 'file' in request.FILES:
            file = request.FILES['file']
            filename = file._name

            image_dir = os.path.join(IMAGE_DIR, filename)
            print(image_dir)
            # for python3
            fp = open('%s' % (image_dir), 'wb')
            for chunk in file.chunks():
                fp.write(chunk)

            fp.close()

            image = Image.objects.create(filename=filename)

            #fs = FileSystemStorage(image_dir)

            # reopen = open('%s' % (image_dir) , 'rb')
            # django_file = File(reopen)

            #image.save()
            #reopen.close()

        return redirect('/upload/')
    return render(request, 'upload.html')

@survey_required
def upload_item(request):
    selected_category1 = 0
    selected_category2 = Item.CATEGORIES[0][1][0][0]
    specified_lower = None
    specified_upper = None
    search_result = []
    if request.method == 'POST':
        category = request.POST['category']
        for i in range(len(Item.CATEGORIES)):
            for c, n in Item.CATEGORIES[i][1]:
                if c == category:
                    selected_category1 = i
                    selected_category2 = c
                    break

        # default image
        filename = "no_image.gif"

        if 'file' in request.FILES:
            file = request.FILES['file']
            if file != '':

                filename = file._name
                filename.replace(" ", "_")

                image_dir = os.path.join(IMAGE_DIR, filename)
                print(image_dir)
                # for python3
                fp = open('%s' % (image_dir), 'wb')
                for chunk in file.chunks():
                    fp.write(chunk)

                fp.close()

        patterns = request.POST['patterns']
        materials = request.POST['materials']
        price = request.POST['price']
        comment = request.POST['comment']

        item = Item(pattern=patterns, material=materials, comment=comment,
                    category=category, price=price, images="http://localhost:8000/static/images/" + filename)

        size = Size()

        if (selected_category1 == 0):
            item.type = 0
            item.sleeve_level = request.POST['sleeve_level']
            item.neck = request.POST['neck_types']
            item.zipper = request.POST['zipper']
            item.button = request.POST['button_top']

            size.length_cm = request.POST['length_cm']
            size.shoulder_cm = request.POST['shoulder_cm']
            size.chest_cm = request.POST['chest_cm']
            size.sleeve_cm = request.POST['sleeve_cm']
            size.letter = request.POST['letter']

        elif (selected_category1 == 1):
            item.type = 1
            item.sleeve_level = request.POST['sleeve_level']
            item.button_outer = request.POST['button_outer']
            item.length_level = request.POST['length_level_outer']
            item.collar = request.POST['collar']
            item.hat = request.POST['hat']
            item.zipper = request.POST['zipper']
            item.padding = request.POST['padding']

            size.length_cm = request.POST['length_cm']
            size.shoulder_cm = request.POST['shoulder_cm']
            size.chest_cm = request.POST['chest_cm']
            size.sleeve_cm = request.POST['sleeve_cm']
            size.letter = request.POST['letter']

        elif (selected_category1 == 2):
            item.type = 2
            item.length_level = request.POST['length_level_bottom']
            item.fit = request.POST['fit_types']

            size.waist_cm = request.POST['waist_cm']
            size.thigh_cm = request.POST['thigh_cm']
            size.crotch_cm = request.POST['crotch_cm']

        item.save()

        # color1 = request.POST['color1']
        # color2 = request.POST['color2']
        # color3 = request.POST['color3']
        # color = Color(item = item, color_id1 = color1, color_id2 = color2,  color_id3 = color3)
        # color.save()

        size.item = item
        size.save()

    return render(request, 'upload_item.html',
                  {'categories': Item.CATEGORIES,
                   'materials': Item.MATERIALS,
                   'neck_types': Item.NECK_TYPES,
                   'patterns': Item.PATTERNS,
                   'fit_types': Item.FIT_TYPES,
                   'selected_category1': selected_category1,
                   'selected_category2': selected_category2,
                   'hanger': request.session.get('hanger', None)})
