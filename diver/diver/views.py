import os
from django.core.files.storage import FileSystemStorage


from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect

from django.shortcuts import render, redirect, render_to_response
from django.core.files import File
from django.core.files import storage

from diver.models import Image
from diver.models import Item
from diver.models import Customer
from diver.settings import IMAGE_DIR
from diver.settings import STATIC_ROOT


__author__ = 'un'


def survey_required(function):
  def wrap(request, *args, **kwargs):


        if Customer.objects.filter(user_id=request.user.id):
            return function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/account')

  wrap.__doc__=function.__doc__
  wrap.__name__=function.__name__
  return wrap

def auth(request):
    return render(request, 'auth.html')

def account(request):
    return render(request, 'account.html')

@survey_required
def main(request):
    if request.method == 'GET':
        items = Item.objects.all()

        # for item in items:
        #     print (item.images)
    return render(request, 'main.html', {'items':items})

def like(request):
    if request.method == 'GET':
        print (request.GET.get('itemID', None))

@survey_required
def search(request):
    category2 = []
    for i in range(len(Item.CATEGORIES)):
        for c,n in Item.CATEGORIES[i][1]:
            category2.append((i,c,n))
    return render(request, 'search.html',
                  {'category1': [(i, Item.CATEGORIES[i][0]) for i in range(len(Item.CATEGORIES))],
                   'category2': category2})

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
