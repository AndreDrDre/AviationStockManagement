from django import template
from django.template.defaultfilters import stringfilter
import urllib
from io import StringIO
import base64
import requests
from django.http import FileResponse, Http404

register = template.Library()


@register.filter
def get64(url):
    pass
