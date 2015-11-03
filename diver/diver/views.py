import os

from django.shortcuts import render, redirect
from django.core.files import File

from diver.models import Image
from diver.settings import IMAGE_DIR
from diver.settings import STATIC_ROOT


__author__ = 'un'


def main(request):
    return render(request, 'main.html')


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

            reopen = open('%s' % (image_dir) , 'rb')
            django_file = File(reopen)

            image = Image(filename=filename, image=django_file)
            image.save()
            reopen.close()

        return redirect('/upload/')
    return render(request, 'upload.html')