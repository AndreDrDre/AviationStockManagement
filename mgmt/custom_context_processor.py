from .models import *


def subject_renderer(request):
    return {"Calicount": Tools_Calibrated.objects.filter(
        user=request.user, calibrated=True, issued=True).count(),
    }


def uncali_renderer(request):
    return {"UnCalicount": Tools_UnCalibrated.objects.filter(user=request.user, issued=True).count(),
            }


def reorder_renderer(request):
    return {"ReOrder": ShoppingList.objects.filter(
        user=request.user, re_orderBoolean=True).count(),
    }
