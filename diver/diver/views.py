import sys,os
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
from diver.models import ItemPref, Color, Size
from diver.settings import IMAGE_DIR
from diver.settings import STATIC_ROOT
from diver.settings import BASE_DIR

sys.path.append(os.path.join(BASE_DIR, '..'))
import algo.item as algo_item
import algo.color as algo_color
import algo.size as algo_size
import algo.category as algo_category

__author__ = 'un'


def survey_required(function):
    def wrap(request, *args, **kwargs):

        if request.session.get('customer_id', None) is not None:
            return function(request, *args, **kwargs)
        elif Customer.objects.filter(user_id=request.user.id).count() > 0:
            request.session['customer_id'] = Customer.objects.filter(user_id=request.user.id)[0].id
            return function(request, *args, **kwargs)
        elif not request.user.is_authenticated():
            return function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/account')

    wrap.__doc__=function.__doc__
    wrap.__name__=function.__name__
    return wrap

def auth(request):
    return render(request, 'auth.html')

def noneCheck(input):
    if input == '':
        return 0
    return input

def account(request):
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        customer = Customer(user_id=request.user, height_cm=180,weight_kg=73,
                            chest_size_cm=50,waist_size_cm=30,sleeve_length_cm=40,
                            leg_length_cm=30,shoes_size_mm=270
                            )
        customer.save()
        
        # Initialize personal preference
        pref = Pref()
        pref.customer = customer
        pref.save()
        algo_item.rating_add_user(customer.id)

        # customers = Customer.objects.filter(user_id=request.user.id)
        try:
            customer = Customer.objects.get(user_id=request.user.id)
        except Customer.DoesNotExist:
            customer = None

        height_cm = request.POST['height_cm']
        weight_kg = request.POST['weight_kg']
        chest_size_cm = request.POST['chest_size_cm']
        waist_size_cm = request.POST['waist_size_cm']
        sleeve_length_cm = request.POST['sleeve_length_cm']
        leg_length_cm = request.POST['leg_length_cm']
        shoes_size_mm = request.POST['shoes_size_mm']
        body_shape = request.POST.get('body_shape','O')

        height_cm = noneCheck(height_cm)
        weight_kg = noneCheck(weight_kg)
        chest_size_cm = noneCheck(chest_size_cm)
        waist_size_cm = noneCheck(waist_size_cm)
        sleeve_length_cm = noneCheck(sleeve_length_cm)
        leg_length_cm = noneCheck(leg_length_cm)
        shoes_size_mm = noneCheck(shoes_size_mm)

        if customer != None :
            customer.height_cm = height_cm
            customer.weight_kg = weight_kg
            customer.chest_size_cm = chest_size_cm
            customer.waist_size_cm = waist_size_cm
            customer.sleeve_length_cm = sleeve_length_cm
            customer.leg_length_cm = leg_length_cm
            customer.shoes_size_mm = shoes_size_mm
            customer.body_shape = body_shape

            customer.save()

        else:

            customer = Customer(user_id=request.user.id, height_cm=height_cm,weight_kg=weight_kg,
                            chest_size_cm=chest_size_cm,waist_size_cm=waist_size_cm,sleeve_length_cm=sleeve_length_cm,
                            leg_length_cm=leg_length_cm, shoes_size_mm=shoes_size_mm, body_shape=body_shape
            )
            customer.save()
    return render(request, 'account.html')

@survey_required
def main(request):
    if request.method == 'GET':
        items = Item.objects.all()
        if request.session.get('customer_id') is not None:
            item_ids = [item.id for item in items]
            item_ids = algo_item.reorder_items(item_ids, request.session['customer_id'], [])
            items = [Item.get(id=id) for id in item_ids]

        # for item in items:
        #     print (item.images)
    return render(request, 'main.html', {'items':items})

def like(request, id, score):
    return (HttpResponse("{} {}".format(id, score)))
    if request.method == 'GET':
        item = Item.objects.filter(id = id)
        if item != []:

            item_pref = ItemPref.objects.filter(item_id = id, user_id = request.user.id)

            if item_pref != []:
                # item 값이 벼하는 시점
                item_pref.scorer = score
                pass
            else:
                # customer = Customer.objects.filter(user_id = request.user.id)
                # customer.like(Item.objects.filter(id = id), like)
                item_pref = ItemPref(item_id = id, user_id = request.user.id, score = score)
            item_pref.save()

    return HttpResponse("recieved" + id)

@survey_required
def search(request):
    selected_category1 = 0
    selected_category2 = Item.CATEGORIES[0][1][0][0]
    specified_lower = None
    specified_upper = None
    search_result = []
    if 'category' in request.GET:
        category = request.GET['category']

        for i in range(len(Item.CATEGORIES)):
            for c,n in Item.CATEGORIES[i][1]:
                if c == category:
                    selected_category1 = i
                    selected_category2 = c
                    break

        items = Item.objects.filter(category=category)
        try:
            specified_lower = int(request.GET['lower'])
            items = items.exclude(price__lte=specified_lower)
        except: pass
        try:
            specified_upper = int(request.GET['upper'])
            items = items.exclude(price__gte=specified_upper)
        except: pass
        search_result = items

    return render(request, 'search.html',
                  {'categories': Item.CATEGORIES,
                   'selected_category1': selected_category1,
                   'selected_category2': selected_category2,
                   'lower': specified_lower,
                   'upper': specified_upper,
                   'search_result': search_result,
                   'hanger': request.session.get('hanger', None)})

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
        return JsonResponse({"result": "ok"})
    else:
        raise SuspiciousMultipartForm()

@survey_required
def upload(request):
    if request.method == 'POST':
        #filename = request.POST["filename"]

        if 'file' in request.FILES:
            file = request.FILES['file']
            filename = file._name

            image_dir = os.path.join(IMAGE_DIR,filename)
            print (image_dir)
            # for python3
            fp = open('%s' % (image_dir) , 'wb')
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


def upload_item(request):

    selected_category1 = 0
    selected_category2 = Item.CATEGORIES[0][1][0][0]
    specified_lower = None
    specified_upper = None
    search_result = []
    if request.method == 'POST':
        category = request.POST['category']
        for i in range(len(Item.CATEGORIES)):
            for c,n in Item.CATEGORIES[i][1]:
                if c == category:
                    selected_category1 = i
                    selected_category2 = c
                    break


        if 'file' in request.FILES:
            file = request.FILES['file']
            filename = file._name
            filename.replace (" ", "_")

            image_dir = os.path.join(IMAGE_DIR,filename)
            print (image_dir)
            # for python3
            fp = open('%s' % (image_dir) , 'wb')
            for chunk in file.chunks():
                fp.write(chunk)

            fp.close()


        patterns = request.POST['patterns']
        materials = request.POST['materials']
        price = request.POST['price']
        comment = request.POST['comment']

        item = Item(pattern= patterns,material=materials, comment=comment,
                    category = category, price = price, images="http://localhost:8000/static/images/"+filename)

        size = Size()

        if(selected_category1 == 0):
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

        elif(selected_category1 == 1):
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

        elif(selected_category1 == 2):
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
