from django import template
from django.template.defaultfilters import stringfilter
import urllib
from io import StringIO
import base64
import requests

register = template.Library()


@register.filter
def get64(url):
    """
    Method returning base64 image data instead of URL
    """
    reqcontent = requests.get(url).content
    base64str = base64.b64encode(reqcontent).decode('utf-8')
    return "data:image/png;base64, " + str(base64str)
