from .models import *


def subject_renderer(request):
    if request.user.is_anonymous:
        context = {}
    else:
        context = {"Calicount": Tools_Calibrated.objects.filter(
            user=request.user, calibrated=True, issued=True).count(),
        }

    return context


def uncali_renderer(request):
    if request.user.is_anonymous:
        context = {}
    else:
        context = {"UnCalicount": Tools_UnCalibrated.objects.filter(user=request.user, issued=True).count(),
                   }

    return context


def reorder_renderer(request):

    if request.user.is_anonymous:
        context = {}
    else:
        context = {"ReOrder": ShoppingList.objects.filter(user=request.user,
                                                          re_orderBoolean=True).count(),
                   }
    return context
