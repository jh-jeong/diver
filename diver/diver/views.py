import os
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse


from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect

from django.shortcuts import render, redirect, render_to_response
from django.core.files import File
from django.core.files import storage

from diver.models import Image
from diver.models import Item
from diver.models import Customer
from diver.models import ItemPref
from diver.settings import IMAGE_DIR
from diver.settings import STATIC_ROOT


__author__ = 'un'


def survey_required(function):
  def wrap(request, *args, **kwargs):

        if Customer.objects.filter(user_id=request.user.id) or not request.user.is_authenticated():
            return function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/account')

  wrap.__doc__=function.__doc__
  wrap.__name__=function.__name__
  return wrap

def auth(request):
    return render(request, 'auth.html')

def account(request):
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        customer = Customer(user_id=request.user, height_cm=180,weight_kg=73,
                            chest_size_cm=50,waist_size_cm=30,sleeve_length_cm=40,
                            leg_length_cm=30, shoes_size_mm=260
                            )
        customer.save()

    return render(request, 'account.html')

@survey_required
def main(request):
    if request.method == 'GET':
        items = Item.objects.all()

        # for item in items:
        #     print (item.images)
    return render(request, 'main.html', {'items':items})

def like(request, id, score):

    if request.method == 'GET':
        item = Item.objects.filter(id = id)
        if item != []:
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
    if request.method == 'POST':
        category = request.POST['category']
        for i in range(len(Item.CATEGORIES)):
            for c,n in Item.CATEGORIES[i][1]:
                if c == category:
                    selected_category1 = i
                    selected_category2 = c
                    break

        items = Item.objects.filter(category=category)
        try:
            specified_lower = int(request.POST['lower'])
            items = items.exclude(price__lte=specified_lower)
        except: pass
        try:
            specified_upper = int(request.POST['upper'])
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
            new_hanger = request.session['hanger']
            new_hanger.append(item_id)
            request.session['hanger'] = new_hanger
        elif action == 'DELETE':
            new_hanger = request.session['hanger']
            new_hanger.remove(item_id)
            request.session['hanger'] = new_hanger
        else:
            raise SuspiciousMultipartForm()
        return HttpResponse("")
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
