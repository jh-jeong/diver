import os
from django.shortcuts import render, redirect
from diver.models import Image
from diver.settings import IMAGE_DIR
from diver.settings import STATIC_URL

__author__ = 'un'


def upload(request):

    if request.method == 'POST':
        #filename = request.POST["filename"]

        if 'file' in request.FILES:
            file = request.FILES['file']
            filename = file._name
            # for python3

            #fullname = os.path.join(IMAGE_DIR,filename)
            #with open(fullname,"w") as fp:
            fp = open('%s' % (filename) , 'wb')
            for chunk in file.chunks():
                fp.write(chunk)
            image = Image(filename=filename)
            image.save()
            fp.close()
        return redirect('/upload/')
    return render(request, 'upload.html')