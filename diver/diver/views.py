import os
from django.core.files.storage import FileSystemStorage

from django.shortcuts import render, redirect
from django.core.files import File
from django.core.files import storage

from diver.models import Image
from diver.models import Item

from diver.settings import IMAGE_DIR
from diver.settings import STATIC_ROOT


__author__ = 'un'

def auth(request):
    return render(request, 'auth.html')

def main(request):

    if request.method == 'GET':
        items = Item.objects.all()

        # for item in items:
        #     print (item.images)
    return render(request, 'main.html', {'items':items})

def like(request):

    if request.method == 'GET':
        print (request.GET.get('itemID', None))

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

    category2 = []
    for i in range(len(Item.CATEGORIES)):
        for c,n in Item.CATEGORIES[i][1]:
            category2.append((i,c,n))
    return render(request, 'search.html', 
        {'category1': [(i, Item.CATEGORIES[i][0]) for i in range(len(Item.CATEGORIES))],
         'category2': category2,
         'selected_category1': selected_category1,
         'selected_category2': selected_category2,
         'lower': specified_lower,
         'upper': specified_upper,
         'search_result': search_result})

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
