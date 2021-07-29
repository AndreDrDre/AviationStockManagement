from django import template
from django.template.defaultfilters import stringfilter
import urllib
from io import StringIO
import base64
import requests
from django.http import FileResponse, Http404
from pdf2image import convert_from_path

register = template.Library()


@register.filter
def get64(path):
    images = convert_from_path(path)
    for i in range(len(images)):
        images[i].save('page' + str(i) + '.jpg', 'JPEG')
        print(images[i])
        # Save pages as images in the pdf
        #

# from pdf2image import convert_from_path
# pages = convert_from_path('pdf_file', 500)

# #Saving pages in jpeg format

# for page in pages:
#     page.save('out.jpg', 'JPEG')
