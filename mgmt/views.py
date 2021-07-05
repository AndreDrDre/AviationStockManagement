# Django Imports
from django.shortcuts import render, redirect
from django.contrib import messages
import django_filters
import datetime
from django.http import HttpResponse, JsonResponse
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import inlineformset_factory

from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404


from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum
from django.db.models import F
from django.db.models import Q
from django.urls import reverse


# Class imports
# from .decorators import unauth_user, allowed_users, admin_only
from .models import *
from .forms import *
from .filters import *
import json
import xlwt


# Create your views here.-------------------#

#login Views-------------------------------------#


def adminpage(request):
    return redirect('adminpage')


def register(request):

    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('signin')

    return render(request, 'mgmt/register.html', {'form': form})


def signin(request):

    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Username or Password is incorrect!')

    return render(request, 'mgmt/login.html')


def logoutUser(request):
    logout(request)
    return redirect('signin')
#-------------------------------------------------#


#Part-Number Placement Logic----------------#

def convertAlpha(string):
    char = ""
    sum = 0

    for x in string:
        if x.isalnum():
            char = "".join([char, x])

    for x in str(char):
        if x.isnumeric():
            sum = sum + int(x)
        elif x.isalpha():
            sum = sum + ord(x)
        else:
            pass
    return int(sum)


def PlaceNewPartNumber(string, listPartNo):
    dictPartNumbers = {}
    listPart = []
    bin_number = ""
    exists = False
    for x in listPartNo:
        dictPartNumbers[x] = convertAlpha(x)

    if string in listPartNo:
        bin_number = 'AZ-' + str(dictPartNumbers[string])
        label = bin_number
        exists = True
    else:
        dictPartNumbers[string] = convertAlpha(string)
        bin_number = 'AZ-' + str(dictPartNumbers[string])
        label = bin_number

    listPart.append(exists)
    listPart.append(bin_number)

    return listPart

#-------------------------------------------#


@login_required(login_url='signin')
def home(request):
    #status bar#
    workorders = WorkOrders.objects.filter(user=request.user)
    workordercount = workorders.filter(status='OPEN').count()
    workordercountclosed = workorders.filter(status='COMPLETED').count()

    order = Parts.objects.filter(user=request.user)
    orderpending = order.filter(recieve_part=False).count()
    reorderparts = ReorderItems.objects.filter(
        user=request.user, reorder_level__gte=F('quantity')).count()

    #status bar#

    context = {

        "workordercount": workordercount,
        "workordercountclosed": workordercountclosed,
        "orderpending": orderpending,
        "reorderparts": reorderparts,
    }
    return render(request, "mgmt/home.html", context)


#Store Logic-------------------------------#

@login_required(login_url='signin')
def store(request):

    #statuc bar#
    queryset = WorkOrders.objects.filter(user=request.user)
    workordercount = queryset.filter(status='OPEN').count()
    workordercountclosed = queryset.filter(status='COMPLETED').count()

    queryset = Parts.objects.filter(user=request.user, recieve_part=False)
    orderpending = queryset.count()

    reorderparts = ReorderItems.objects.filter(
        user=request.user, reorder_level__gte=F('quantity')).count()
    #statuc bar#

    context = {
        "workordercount": workordercount,
        "workordercountclosed": workordercountclosed,
        "orderpending": orderpending,
        "reorderparts": reorderparts,

    }
    return render(request, "mgmt/store.html", context)


@login_required(login_url='signin')
def Rinventory(request):
    #statuc bar#
    querysetW = WorkOrders.objects.filter(user=request.user)
    workordercount = querysetW.filter(status='OPEN').count()
    workordercountclosed = querysetW.filter(status='COMPLETED').count()

    querysetS = Parts.objects.filter(user=request.user)
    orderpending = querysetS.filter(recieve_part=False).count()

    reorderparts = ReorderItems.objects.filter(
        user=request.user, reorder_level__gte=F('quantity')).count()

    #statuc bar#
    queryset = Parts.objects.filter(~Q(condition="REPAIRABLE"),
                                    tail_number__name__startswith="N", user=request.user, Quarentine=False, Historical=False,
                                    recieve_part=True,).order_by('date_received').reverse()

    #filter--------------------------------------------------------#
    filtype = "Reserved"
    Partfilter = ReservedFilter(request.GET, queryset=queryset)
    queryset = Partfilter.qs

    #---------------------------------------------------------------#

    for q in queryset:
        if q.quantity == 0 and q.order_quantity == 0:
            q.bin_number = None
            q.save(update_fields=['bin_number'])
            q.Historical = True
            q.save(update_fields=['Historical'])

    context = {
        "workordercount": workordercount,
        "workordercountclosed": workordercountclosed,
        "orderpending": orderpending,
        "queryset": queryset,
        "partfilter": Partfilter,
        "reorderparts": reorderparts,
    }
    return render(request, "PartsFolder/RInventory.html", context)


@login_required(login_url='signin')
def Qinventory(request):

    #statuc bar#
    queryset = WorkOrders.objects.filter(user=request.user)
    workordercount = queryset.filter(status='OPEN').count()
    workordercountclosed = queryset.filter(status='COMPLETED').count()

    querysetS = Parts.objects.filter(user=request.user)
    orderpending = querysetS.filter(recieve_part=False).count()

    reorderparts = ReorderItems.objects.filter(
        user=request.user, reorder_level__gte=F('quantity')).count()

    #statuc bar#

    # This queryset recieves all the Quarentine Inventory---------------#

    queryset = Parts.objects.filter(user=request.user, Quarentine=True, Historical=False, recieve_part=True,
                                    Repaired=False).order_by('date_received').reverse()

    # ------------------------------------------------------------------#

    querysetShop = Parts.objects.filter(user=request.user, Quarentine=True, Historical=False, recieve_part=True,
                                        repaired_by='SHOP', Repaired=True).order_by('date_received').reverse()

    querysetInhouse = Parts.objects.filter(user=request.user, Quarentine=True, Historical=False, recieve_part=True,
                                           repaired_by='INHOUSE', Repaired=True).order_by('date_received').reverse()

    Partfilter = QuaratineFilter(request.GET, queryset=queryset)
    queryset = Partfilter.qs

    context = {
        "workordercount": workordercount,
        "workordercountclosed": workordercountclosed,
        "orderpending": orderpending,
        "reorderparts": reorderparts,
        "queryset": queryset,
        "partfilter": Partfilter,
        "querysetShop": querysetShop,
        "querysetInhouse": querysetInhouse,
    }
    return render(request, "PartsFolder/QInventory.html", context)


@login_required(login_url='signin')
def repair(request, pk):

    queryset = Parts.objects.get(user=request.user, id=pk)

    form = RepairForm(instance=queryset)

    if request.method == 'POST':
        form = RepairForm(request.POST, instance=queryset)

        if form.is_valid():
            queryset.Repaired = True
            queryset.save(update_fields=['Repaired'])
            if queryset.repaired_by == 'SHOP':
                queryset.delete()
            else:
                form.save()

            return redirect('Qinventory')

    context = {"form": form, "queryset": queryset}

    return render(request, "mgmt/repair.html", context)


@login_required(login_url='signin')
def repairReturn(request, pk):

    queryset = Parts.objects.get(user=request.user, id=pk)
    conditionCheck = queryset.condition

    if request.method == 'POST':

        form = repairReturnForm(conditionCheck,
                                request.POST, request.FILES, instance=queryset)

        if form.is_valid():

            queryset.condition = 'SV'
            queryset.tail_number = 'Stock'
            queryset.Repaired = False
            queryset.recieve_part = False
            queryset.Quarentine = False

            queryset.date_received = timezone.now()
            queryset.save(update_fields=['condition'])
            queryset.save(update_fields=['Repaired'])
            queryset.save(update_fields=['tail_number'])
            queryset.save(update_fields=['recieve_part'])
            queryset.save(update_fields=['date_received'])

            form.save()
            return redirect('instructions', pk=queryset.id)

    else:
        form = repairReturnForm(conditionCheck, instance=queryset)

        # form.fields["bin_number"].queryset = Parts.objects.filter()

    context = {"form": form, "queryset": queryset, }

    return render(request, "PartsFolder/receiveRepair.html", context)


@login_required(login_url='signin')
def inventory(request):
    type = ''
    #statuc bar#
    querysetW = WorkOrders.objects.filter(user=request.user)
    workordercount = querysetW.filter(status='OPEN').count()
    workordercountclosed = querysetW.filter(status='COMPLETED').count()

    querysetS = Parts.objects.filter(user=request.user)
    orderpending = querysetS.filter(recieve_part=False).count()

    reorderparts = ReorderItems.objects.filter(
        user=request.user, reorder_level__gte=F('quantity')).count()

    #statuc bar#
    queryset = Parts.objects.filter(user=request.user, tail_number__name__contains='Stock', Historical=False, Quarentine=False,
                                    recieve_part=True).order_by('date_received').reverse()

    # condition='REPAIRABLE', Historical=False, recieve_part=True, Repaired=False)

    for q in queryset:
        if q.quantity == 0 and q.order_quantity == 0:
            q.bin_number = None
            q.save(update_fields=['bin_number'])
            q.Historical = True
            q.save(update_fields=['Historical'])

    Partfilter = PartsFilter(request.GET, queryset=queryset)
    queryset = Partfilter.qs

    if queryset.count() == 1:
        for i in queryset:
            checkerQ = i.SRN

    context = {
        "workordercount": workordercount,
        "workordercountclosed": workordercountclosed,
        "orderpending": orderpending,
        "queryset": queryset,
        "partfilter": Partfilter,
        "reorderparts": reorderparts
    }
    return render(request, "PartsFolder/Inventory.html", context)


@login_required(login_url='signin')
def addToInventory(request, Type):

    print("somthing")

    check = 0
    checkType = 0

    # form = AddInventory(Type, request.POST or None, request.FILES or None)

    #The cancel Button---------#

    if Type == "Stock":
        check = 0
    elif Type == "Reserved":
        check = 1
    else:  # Type = "RemoveFromAircraft"
        check = 2
    #The cancel Button------------#

    if request.method == 'POST':
        # data = request.POST
        form = AddInventory(Type, request.POST, request.FILES)

        if form.is_valid():
            print(request.is_ajax())

            if Type == "Reserved":
                tail_number = form.cleaned_data['tail_number']
                vendor = form.cleaned_data['vendor']
                order_quantity = form.cleaned_data['order_quantity']
                price = form.cleaned_data['price']
                purchase_order_number = form.cleaned_data['purchase_order_number']
                invoice_number = form.cleaned_data['invoice_number']
                expiry_date = forms.cleaned_data['expiry_date']

            elif Type == "Stock":
                tail_number = TailNumber.objects.all().reverse()[0]
                vendor = form.cleaned_data['vendor']
                order_quantity = form.cleaned_data['order_quantity']
                price = form.cleaned_data['price']
                purchase_order_number = form.cleaned_data['purchase_order_number']
                invoice_number = form.cleaned_data['invoice_number']
                expiry_date = forms.cleaned_data['expiry_date']

            else:  # Type = "RemoveFromAircraft"
                vendor = ""
                tail_number = form.cleaned_data['tail_number']
                order_quantity = 1
                workorder = form.cleaned_data['workorder']
                jobCardNumber = form.cleaned_data['jobCardNumber']
                checkType = 1

            condition = form.cleaned_data['condition']
            part_type = form.cleaned_data['part_type']
            description = form.cleaned_data['description']
            part_number = form.cleaned_data['part_number']
            indentifier = form.cleaned_data['indentifier']
            cert_document = form.cleaned_data['cert_document']
            inspector = form.cleaned_data['inspector']

            # If the part has been removed from an aircraft under a workorder
            if checkType == 1:
                if part_type == 'Rotable' or part_type == 'Tires':
                    p = Parts(part_type=part_type,
                              description=description,
                              part_number=part_number,
                              vendor=vendor,
                              serial_number=indentifier,
                              cert_document=cert_document,
                              quantity=order_quantity,
                              tail_number=TailNumber.objects.all().reverse()[
                                  0],
                              inspector=inspector,
                              condition=condition,
                              date_received=timezone.now(),
                              Historical=False,
                              recieve_part=True,
                              Quarentine=False,
                              user=request.user
                              )
                    p.save()

                    PartWorkOrders.objects.create(
                        part=p, workorder=workorder, jobCardNumber=jobCardNumber, receivedRepair=True,
                        cert_document=cert_document, removed_from=tail_number, removed_by=inspector)

                    # Now we need establish the condition of the removed part( serviceable or not)

                    if p.condition == "REPAIRABLE":
                        p.Quarentine = True
                        p.save(update_fields=["Quarentine"])
                        p.cert_document.save()

                        if request.is_ajax():
                            # form.save()
                            return JsonResponse({'success': 'Adding Removed Part to Quarentine Database...', 'redirect_to': reverse('Qinventory')})
                        # return redirect('Qinventory')
                    else:
                        p.tail_number.name = "Stock"
                        p.save(update_fields=["tail_number"])

                        if request.is_ajax():
                            # form.save()
                            return JsonResponse({'success': 'Adding Removed Part to Stock Database...', 'redirect_to': reverse('instructions', kwargs={'pk': p.id})})
                        # return redirect('instructions', pk=p.id)

                    # removed parts that are not serialised (AGS Parts)
                else:
                    p = Parts(part_type=part_type,
                              description=description,
                              part_number=part_number,
                              vendor=vendor,
                              batch_no=indentifier,
                              cert_document=cert_document,
                              quantity=order_quantity,
                              tail_number=TailNumber.objects.all().reverse()[
                                  0],
                              inspector=inspector,
                              condition=condition,
                              date_received=timezone.now(),
                              Historical=False,
                              recieve_part=True,
                              Quarentine=False,
                              user=request.user
                              )
                    p.save()
                    PartWorkOrders.objects.create(
                        part=p, workorder=workorder, jobCardNumber=jobCardNumber, receivedRepair=True,
                        cert_document=cert_document, removed_from=tail_number, removed_by=inspector)
                    if p.condition == "REPAIRABLE":
                        p.Quarentine = True
                        p.save(update_fields=["Quarentine"])
                        if request.is_ajax():
                            return JsonResponse({'success': 'Adding Removed Part to Quarentine Database...', 'redirect_to': reverse('Qinventory')})
                        # return redirect('Qinventory')
                    else:
                        p.tail_number.name = "Stock"
                        p.save(update_fields=["tail_number"])
                        if request.is_ajax():
                            # form.save()
                            return JsonResponse({'success': 'Adding Removed Part to Stock Database...', 'redirect_to': reverse('instructions', kwargs={'pk': p.id})})
                        # return redirect('inventory')

            # Parts not removed from an aircraft! Cosignment added Parts
            else:
                if part_type == 'Rotable' or part_type == 'Tires':
                    p = Parts(part_type=part_type,
                              description=description,
                              part_number=part_number,
                              vendor=vendor,
                              serial_number=indentifier,
                              cert_document=cert_document,
                              quantity=1,
                              tail_number=tail_number,
                              inspector=inspector,
                              purchase_order_number=purchase_order_number,
                              invoice_number=invoice_number,
                              condition=condition,
                              date_received=timezone.now(),
                              Historical=False,
                              price=price,
                              expiry_date=expiry_date,
                              user=request.user
                              )

                    p.save()
                    if request.is_ajax():
                        if p.tail_number.name == "Stock":
                            # form.save()
                            return JsonResponse({'success': 'Adding Part to Stock Database...', 'redirect_to': reverse('instructions', kwargs={'pk': p.id})})
                        else:
                            # form.save()
                            return JsonResponse({'success': 'Adding Part to Reserved Stock Database...', 'redirect_to': reverse('instructions', kwargs={'pk': p.id})})
                    # return redirect('instructions', pk=p.id)

                else:
                    p = Parts(part_type=part_type,
                              description=description,
                              part_number=part_number,
                              vendor=vendor,
                              batch_no=indentifier,
                              cert_document=cert_document,
                              quantity=order_quantity,
                              tail_number=tail_number,
                              inspector=inspector,
                              purchase_order_number=purchase_order_number,
                              invoice_number=invoice_number,
                              condition=condition,
                              date_received=timezone.now(),
                              Historical=False,
                              price=price,
                              expiry_date=expiry_date,
                              user=request.user
                              )

                    p.save()
                    if request.is_ajax():
                        if p.tail_number.name == "Stock":
                            # form.save()
                            return JsonResponse({'success': 'Adding Part to Stock Database...', 'redirect_to': reverse('instructions', kwargs={'pk': p.id})})
                        else:
                            # form.save()
                            return JsonResponse({'success': 'Adding Part to Reserved Stock Database...', 'redirect_to': reverse('instructions', kwargs={'pk': p.id})})
                    # return redirect('instructions', pk=p.id)
    else:
        form = AddInventory(Type)
        print(form.errors)
    context = {"form": form, "check": check}
    if request.is_ajax():
        # form.save()
        return JsonResponse({'error': True})
    return render(request, "PartsFolder/add_Inventory.html", context)


@login_required(login_url='signin')
def addToQuarentine(request):

    form = addQuaretineInventory(
        request.POST or None, request.FILES or None)

    # we need to chage the quarentine component

    if form.is_valid():

        order_quantity = form.cleaned_data['condition']
        condition = form.cleaned_data['condition']
        part_type = form.cleaned_data['part_type']
        description = form.cleaned_data['description']
        part_number = form.cleaned_data['part_number']
        indentifier = form.cleaned_data['indentifier']
        cert_document = form.cleaned_data['cert_document']
        inspector = form.cleaned_data['inspector']

        if part_type == 'Rotable' or part_type == 'Tires':
            p = Parts(part_type=part_type,
                      description=description,
                      part_number=part_number,
                      ipc_reference="",
                      serial_number=indentifier,
                      cert_document=cert_document,
                      quantity=1,
                      inspector=inspector,
                      condition=condition,
                      date_received=timezone.now(),
                      Historical=False,
                      recieve_part=True,
                      Quarentine=True,
                      user=request.user
                      )
            p.save()
            if request.is_ajax():
                return JsonResponse({'success': 'Adding Removed Part to Quarentine Database...', 'redirect_to': reverse('Qinventory')})
            # return redirect('Qinventory')
        else:
            p = Parts(part_type=part_type,
                      description=description,
                      part_number=part_number,
                      ipc_reference="",
                      batch_no=indentifier,
                      cert_document=cert_document,
                      quantity=order_quantity,
                      inspector=inspector,
                      condition=condition,
                      date_received=timezone.now(),
                      Historical=False,
                      recieve_part=True,
                      Quarentine=True,
                      user=request.user
                      )
            p.save()
            if request.is_ajax():
                return JsonResponse({'success': 'Adding Part to Quarentine Database...', 'redirect_to': reverse('Qinventory')})
            # return redirect('Qinventory')

    context = {"form": form}
    if request.is_ajax():
        return JsonResponse({'error': True})

    return render(request, "PartsFolder/addToQuarentine.html", context)


@login_required(login_url='signin')
def interimtransfer(request):

    return render(request, 'PartsFolder/InterimTransfer.html')


@login_required(login_url='signin')
def createneworder(request, pk):

    part = Parts.objects.get(user=request.user, id=pk)
    createForm = CreateNewOrder(instance=part)

    if request.method == 'POST':
        # senidng new data into a pre exisitng field.
        createForm = CreateNewOrder(request.POST, instance=part)
        if createForm.is_valid():

            part.recieve_part = False
            part.save(update_fields=['recieve_part'])

            createForm.save()  # save the form into the database
            return redirect('orderpart')
    else:
        createForm = CreateNewOrder()
        context = {
            'createForm': createForm,
            'part': part,
        }

    return render(request, 'OrdersFolder/createneworder.html', context)


@login_required(login_url='signin')
def issuePart(request, pk):
    check = ""
    queryset = Parts.objects.get(user=request.user, id=pk)
    check = queryset.tail_number
    sender = queryset.id

    form = issueWorkForm(instance=queryset, user=request.user)

    if request.method == 'POST':

        form = issueWorkForm(
            request.POST, instance=queryset, user=request.user)
        if form.is_valid():

            quantity = queryset.issue_quantity

            if quantity > queryset.quantity:
                pass

            else:
                queryset.quantity -= quantity
                queryset.save(update_fields=['quantity'])
                form.save()

            if queryset.tail_number == 'Stock':
                quersetReOrder = ReorderItems.objects.all()
                for x in quersetReOrder:
                    if x.part_number == queryset.part_number:
                        x.quantity = x.quantity - queryset.issue_quantity

                        x.save(update_fields=['quantity'])

            if check == 'Stock':
                return redirect('inventory')
            else:
                return redirect('Rinventory')

    context = {'form': form, 'queryset': queryset, }
    return render(request, 'PartsFolder/issuePart.html', context)


@login_required(login_url='signin')
def reorder_level(request, pk):

    queryset = ReorderItems.objects.get(user=request.user, id=pk)

    form = ReorderLevelForm(request.POST or None, instance=queryset)

    if form.is_valid():
        form.save()

        # instance = form.save(commit=False)
        # instance.save()
        if request.is_ajax():
            return JsonResponse({'success': 'Updating Re-Order Level...', 'redirect_to': reverse('reorderParts')})
        return redirect('reorderParts')

    else:
        form = ReorderLevelForm(request.POST or None, instance=queryset)

    context = {
        'queryset': queryset,
        'form': form,
    }
    return render(request, "OrdersFolder/re-order.html", context)


@login_required(login_url='signin')
def edit_part(request, pk):

    queryset = Parts.objects.get(user=request.user, id=pk)

    form = EditPartForm(request.POST or None, instance=queryset)

    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()

        return redirect('Rinventory')
    context = {
        'queryset': queryset,
        'form': form,
    }
    return render(request, "PartsFolder/editpart.html", context)
#------------------------------------------#

#Historical--------------------------------#


@login_required(login_url='signin')
def historical_inventory(request):
    #statuc bar#
    querysetW = WorkOrders.objects.filter(user=request.user)
    workordercount = querysetW.filter(status='OPEN').count()
    workordercountclosed = querysetW.filter(status='COMPLETED').count()

    querypendingorders = Parts.objects.filter(user=request.user)
    orderpending = querypendingorders.filter(recieve_part=False).count()

    reorderparts = ReorderItems.objects.filter(
        user=request.user, reorder_level__gte=F('quantity')).count()

    #status end#

    # All parts with which have been exhausted through work-order assigning
    queryset = Parts.objects.filter(user=request.user, Historical=True)

    # completed work-orders
    querysetclosed = querysetW.filter(status='COMPLETED')

    Partfilter = PartsFilter(request.GET, queryset=queryset)
    queryset = Partfilter.qs

    myFilter_workorder = WorkOrderFilter(request.GET, queryset=querysetclosed)
    querysetclosed = myFilter_workorder.qs

    context = {
        "workordercount": workordercount,
        "workordercountclosed": workordercountclosed,
        "orderpending": orderpending,
        "queryset": queryset,
        "partfilter": Partfilter,
        "reorderparts": reorderparts,
        "querysetclosed": querysetclosed,
        "workOrderFilter": myFilter_workorder,

    }
    return render(request, "PartsFolder/historical_Inventory.html", context)


@login_required(login_url='signin')
def historialWO(request, pk):

    # workorder_specific = WorkOrders.objects.get(id=pk)
    # partsIssue = workorder_specific.partworkorders_set.all()
    counter = 0
    partspecific = Parts.objects.get(user=request.user, id=pk, Historical=True)
    parthistory = partspecific.partworkorders_set.all().filter(receivedRepair=False)
    parthistoryRemoved = partspecific.partworkorders_set.all().filter(receivedRepair=True)

    for part in parthistory:
        counter += part.issue_quantity

    context = {
        'parthistory': parthistory,
        'partspecific': partspecific,
        'counter': counter,
        "parthistoryRemoved": parthistoryRemoved,

    }
    return render(request, "PartsFolder/partshistory.html", context)
#------------------------------------------#

#Work-Order Logic Start--------------------#


@login_required(login_url='signin')
def workorders(request):

    #statuc bar#
    queryset = WorkOrders.objects.filter(user=request.user)
    workordercount = queryset.filter(status='OPEN').count()
    workordercountclosed = queryset.filter(status='COMPLETED').count()

    order = Parts.objects.filter(user=request.user)
    orderpending = order.filter(recieve_part=False).count()
    reorderparts = ReorderItems.objects.filter(
        user=request.user, reorder_level__gte=F('quantity')).count()

    #statuc bar#

    #Display only open workorders#
    querysetopen = queryset.filter(status='OPEN')
    #----------------------------#

    # forms
    form = CreateWorkorder(request.POST or None)
    form.instance.user = request.user

    if form.is_valid():
        form.save()
        return redirect('workorders')
    #----------------------------#

    #Filters#
    myFilter_workorder = WorkOrderFilter(
        request.GET, queryset=querysetopen)
    querysetopen = myFilter_workorder.qs

    #----------------------------#
    context = {
        "workordercount": workordercount,
        "querysetopen": querysetopen,
        "workordercountclosed": workordercountclosed,
        "form": form,
        "myfilter": myFilter_workorder,
        "orderpending": orderpending,
        "reorderparts": reorderparts,
    }
    return render(request, "WorkorderFolder/workorder.html", context)


@login_required(login_url='signin')
def partslink(request, pk, Type):
    total = 0
    #status bar#
    queryset = WorkOrders.objects.filter(user=request.user)
    workordercount = queryset.filter(status='OPEN').count()
    workordercountclosed = queryset.filter(status='COMPLETED').count()
    order = Parts.objects.filter(user=request.user)
    orderpending = order.filter(recieve_part=False).count()

    reorderparts = ReorderItems.objects.filter(
        user=request.user, reorder_level__gte=F('quantity')).count()

    #status bar#

    # Link To Specific WorkOrder
    workorder_specific = WorkOrders.objects.get(user=request.user, id=pk)
    querysetDisplay = WorkOrders.objects.get(user=request.user, id=pk)

    # return all parts related to work id
    partsIssue = workorder_specific.partworkorders_set.filter(
        receivedRepair=False).order_by('created_at').reverse()

    filter = WorkOrderLinkPartFilter(request.GET, queryset=partsIssue)
    partsIssue = filter.qs

    partsReceived = workorder_specific.partworkorders_set.filter(
        receivedRepair=True).order_by('created_at').reverse()

    for parts in partsIssue:
        total += parts.price * parts.issue_quantity

    # singletotal = part.price * part.issue_quantity

    toolscali = workorder_specific.tools_calibrated_set.all()
    toolsUncali = workorder_specific.tools_uncalibrated_set.all()

    # Displaying the workorder we are linking too
    workordernumber = workorder_specific.workorder_number

    context = {
        "workordercount": workordercount,
        "workordernumber": workordernumber,
        "workordercountclosed": workordercountclosed,
        "partsIssue": partsIssue,
        "UnCali": toolsUncali,
        "Cali": toolscali,
        "orderpending": orderpending,
        "reorderparts": reorderparts,
        "querysetDisplay": querysetDisplay,
        "total": total,
        "partsReceived": partsReceived,
        "filter": filter,


    }

    if Type == "NotHistorical":
        return render(request, "WorkorderFolder/work-Orderlink.html", context)
    else:
        return render(request, "WorkorderFolder/work-order-history.html", context)


@login_required(login_url='signin')
def change_order_status(request, pk):

    workorder_specific = WorkOrders.objects.get(user=request.user, id=pk)
    workorder_specific.status = 'COMPLETED' if workorder_specific.status == 'OPEN' else 'OPEN'
    workorder_specific.save(update_fields=['status'])

    workorder_specific.date_closed = timezone.now()
    workorder_specific.save(update_fields=['date_closed'])

    #Break the link to tools once a work-order has been completed#
    toolsCali = workorder_specific.tools_calibrated_set.all()
    if toolsCali.count() > 0:
        for tool in toolsCali:
            tool.issued = False
            tool.save(update_fields=['issued'])
            # toolsCali.workorder_no = None
            tool.workorder_no = None
            tool.save(update_fields=['workorder_no'])

    toolsUncali = workorder_specific.tools_uncalibrated_set.all()
    if toolsUncali.count() > 0:
        for toolun in toolsUncali:
            toolun.issued = False
            toolun.save(update_fields=['issued'])
            # toolsUncali.workorder_no = None
            toolun.workorder_no = None

            toolun.save(update_fields=['workorder_no'])

    #------------------------------------------------------------#

    messages.success(request, 'Test number {} {} successfully'.format(
        id, workorder_specific.status))

    exportPDForder(request)

    return redirect('workorders')


@login_required(login_url='signin')
def changeWorkOrderCali(request, pk):
    calitool = Tools_Calibrated.objects.get(user=request.user, id=pk)
    formissueCali = CreateWorkOrderFormCali(instance=calitool)

    if request.method == 'POST':
        if "CancelIssue" in request.POST:
            return redirect('workorders')

        formissueCali = CreateWorkOrderFormCali(
            request.POST, instance=calitool)
        if formissueCali.is_valid():
            if "SaveIssue" in request.POST:
                calitool.issued = True
                calitool.save(update_fields=['issued'])
                formissueCali.save()
                return redirect('workorders')

    context = {'formissueCali': formissueCali, "calitool": calitool}
    return render(request, 'ToolsFolder/issueworkorderCali.html', context)


@login_required(login_url='signin')
def changeWorkOrderUnCali(request, pk):
    Uncalitool = Tools_UnCalibrated.objects.get(user=request.user, id=pk)
    formissueUnCali = CreateWorkOrderFormUnCali(instance=Uncalitool)

    if request.method == 'POST':

        if "CancelIssue" in request.POST:
            return redirect('workorders')
        # senidng new data into a pre exisitng field.
        formissueUnCali = CreateWorkOrderFormUnCali(
            request.POST, instance=Uncalitool)
        if formissueUnCali.is_valid():
            if "SaveIssue" in request.POST:
                Uncalitool.issued = True
                Uncalitool.save(update_fields=['issued'])
                Uncalitool.save()  # save the form into the database
                return redirect('workorders')  # redirect to home page

    context = {'formissueUnCali': formissueUnCali,
               'Uncalitool': Uncalitool}
    return render(request, 'mgmt/issueUncali.html', context)


@login_required(login_url='signin')
def sendhometoolCali(request, pk):
    calitool = Tools_Calibrated.objects.get(user=request.user, id=pk)
    calitool.workorder_no = None
    calitool.save(update_fields=['workorder_no'])
    calitool.issued = 'False'
    calitool.save(update_fields=['issued'])
    return redirect('workorders')


@login_required(login_url='signin')
def sendhometoolUnCali(request, pk):
    Uncalitool = Tools_UnCalibrated.objects.get(user=request.user, id=pk)
    Uncalitool.workorder_no = None
    Uncalitool.save(update_fields=['workorder_no'])
    Uncalitool.issued = 'False'
    Uncalitool.save(update_fields=['issued'])
    return redirect('workorders')
#------------------------------------------#

# Order Parts Logic-----------------------#


@login_required(login_url='signin')
def orderhistory(request):

    #statuc bar#
    workqueryset = WorkOrders.objects.filter(user=request.user)
    workordercount = workqueryset.filter(status='OPEN').count()
    workordercountclosed = workqueryset.filter(status='COMPLETED').count()

    order = Parts.objects.filter(user=request.user)
    orderpending = order.filter(recieve_part=False).count()

    reorderparts = ReorderItems.objects.filter(
        user=request.user, reorder_level__gte=F('quantity')).count()

    #statuc bar#

    query = OrderHistory.objects.filter(
        user=request.user).order_by('date_ordered').reverse()

    myFilter = OHFilter(request.GET, queryset=query)
    query = myFilter.qs
    # filter

    context = {
        "query": query,
        "myFilter": myFilter,
        "workordercount": workordercount,
        "workordercountclosed": workordercountclosed,
        "orderpending": orderpending,
        "reorderparts": reorderparts,
    }

    return render(request, "OrdersFolder/orderhistory.html", context)


@login_required(login_url='signin')
def waybill(request, pk):
    placeholder = ""
    waybill = ""
    string = 'https://www.google.com/search?q='
    queryset = Parts.objects.get(user=request.user, id=pk)
    form = waybillForm(instance=queryset)

    if request.method == 'POST':

        form = waybillForm(
            request.POST, instance=queryset)

        if form.is_valid():

            queryset.urlWayBill = string + form.cleaned_data['waybill']
            form.save()

            return redirect('orderpart')

    context = {"queryset": queryset, "form": form}

    return render(request, "OrdersFolder/waybill.html", context)


@login_required(login_url='signin')
def deletepart(request, pk):
    part = Parts.objects.get(user=request.user, id=pk)
    part.delete()

    if part.recieve_part == False:
        return redirect('orderpart')
    else:
        if part.tail_number.name == 'Stock':
            return redirect('inventory')
        if part.tail_number.name != 'Stock' and part.condition != 'REPAIRABLE':
            return redirect('Rinventory')
        if part.condition == 'REPAIRABLE':
            return redirect('Qinventory')


@login_required(login_url='signin')
def pricechange(request, pk):

    queryset = Parts.objects.get(user=request.user, id=pk)
    form = PriceForm(instance=queryset)

    if request.method == 'POST':

        form = PriceForm(
            request.POST, instance=queryset)

        if form.is_valid():
            form.save()

            return redirect('orderpart')

    context = {"queryset": queryset, "form": form}
    return render(request, "PartsFolder/pricechange.html", context)


@login_required(login_url='signin')
def quickOrder(request, pk):

    try:
        queryset = ReorderItems.objects.get(user=request.user, id=pk)
    except queryset.DoesNotExist:
        queryset = None

    form = ReOrderForm(request.POST or None)

    if form.is_valid():

        orderedBy = form.cleaned_data['ordered_by']
        orderQTY = form.cleaned_data['orderQTY']
        tail_number = form.cleaned_data['tail_number']

        description = queryset.description
        part_number = queryset.part_number
        order_quantity = orderQTY
        ipc_reference = queryset.ipc_reference
        ordered_by = orderedBy
        part_type = queryset.part_type

        if part_type == 'Rotable' or part_type == 'Tires':
            for count in range(order_quantity):
                p = Parts(description=description,
                          part_number=part_number,
                          order_quantity=1,
                          ipc_reference=ipc_reference,
                          date_ordered=timezone.now(),
                          tail_number=tail_number,
                          ordered_by=ordered_by,
                          part_type=part_type,
                          Historical=False,
                          user=request.user)
                p.save()

            h = OrderHistory(description=description,
                             part_number=part_number,
                             order_quantity=order_quantity,
                             ipc_reference=ipc_reference,
                             date_ordered=timezone.now(),
                             tail_number=tail_number,
                             ordered_by=ordered_by,
                             part_type=part_type,
                             user=request.user)
            h.save()
            if request.is_ajax():
                if p.tail_number.name == "Stock":
                    return JsonResponse({'success': 'Placing new Stock Order...', 'redirect_to': reverse('reorderParts')})
                else:
                    return JsonResponse({'success': 'Placing new Reserved Stock Order......', 'redirect_to': reverse('reorderParts')})
            return redirect('reorderParts')

        else:
            p = Parts(description=description,
                      part_number=part_number,
                      order_quantity=order_quantity,
                      ipc_reference=ipc_reference,
                      date_ordered=timezone.now(),
                      tail_number=tail_number,
                      ordered_by=ordered_by,
                      part_type=part_type,
                      Historical=False,
                      user=request.user)
            p.save()

            h = OrderHistory(description=description,
                             part_number=part_number,
                             order_quantity=order_quantity,
                             ipc_reference=ipc_reference,
                             date_ordered=timezone.now(),
                             tail_number=tail_number,
                             ordered_by=ordered_by,
                             part_type=part_type,
                             user=request.user)
            h.save()
            if request.is_ajax():
                if p.tail_number.name == "Stock":
                    return JsonResponse({'success': 'Placing new Stock Order...', 'redirect_to': reverse('reorderParts')})
                else:
                    return JsonResponse({'success': 'Placing new Reserved Stock Order......', 'redirect_to': reverse('reorderParts')})

            return redirect('reorderParts')

    context = {"form": form, "queryset": queryset}
    if request.is_ajax():
        return JsonResponse({'error': True})

    return render(request, "OrdersFolder/re-order.html", context)


@login_required(login_url='signin')
def orderpart(request):

    #statuc bar#
    workqueryset = WorkOrders.objects.filter(user=request.user)
    workordercount = workqueryset.filter(status='OPEN').count()
    workordercountclosed = workqueryset.filter(status='COMPLETED').count()

    order = Parts.objects.filter(user=request.user)
    orderpending = order.filter(recieve_part=False).count()

    reorderparts = ReorderItems.objects.filter(
        user=request.user, reorder_level__gte=F('quantity')).count()

    #statuc bar#

    queryset = Parts.objects.filter(user=request.user, recieve_part=False)

    #Filters----------------------#
    myFilter_order = CreateOrderFilter(request.GET, queryset=queryset)
    queryset = myFilter_order.qs
    #----------------------------#

    form = CreateOrder(request.POST or None)

    if form.is_valid():

        description = form.cleaned_data['description']
        part_number = form.cleaned_data['part_number']
        order_quantity = form.cleaned_data['order_quantity']
        ipc_reference = form.cleaned_data['ipc_reference']

        tail_number = form.cleaned_data['tail_number']
        ordered_by = form.cleaned_data['ordered_by']
        part_type = form.cleaned_data['part_type']

        if part_type == 'Rotable' or part_type == 'Tires':

            for count in range(order_quantity):
                p = Parts(description=description,
                          part_number=part_number,
                          order_quantity=1,
                          ipc_reference=ipc_reference,
                          date_ordered=timezone.now(),
                          tail_number=tail_number,
                          ordered_by=ordered_by,
                          part_type=part_type,
                          Historical=False,
                          user=request.user)
                p.save()

            h = OrderHistory(description=description,
                             part_number=part_number,
                             order_quantity=order_quantity,
                             ipc_reference=ipc_reference,
                             date_ordered=timezone.now(),
                             tail_number=tail_number,
                             ordered_by=ordered_by,
                             part_type=part_type,
                             user=request.user)
            h.save()

        else:
            p = Parts(description=description,
                      part_number=part_number,
                      order_quantity=order_quantity,
                      ipc_reference=ipc_reference,
                      date_ordered=timezone.now(),
                      tail_number=tail_number,
                      ordered_by=ordered_by,
                      part_type=part_type,
                      Historical=False,
                      user=request.user)
            p.save()

            h = OrderHistory(description=description,
                             part_number=part_number,
                             order_quantity=order_quantity,
                             ipc_reference=ipc_reference,
                             date_ordered=timezone.now(),
                             tail_number=tail_number,
                             ordered_by=ordered_by,
                             part_type=part_type,
                             user=request.user)
            h.save()

            # Add to Re-order Items

        return redirect('orderpart')

    context = {
        "form": form,
        "queryset": queryset,
        "workordercountclosed": workordercountclosed,
        "workordercount": workordercount,
        "myfilter": myFilter_order,
        "orderpending": orderpending,
        "reorderparts": reorderparts,
    }
    return render(request, "OrdersFolder/orderpart.html", context)


@login_required(login_url='signin')
def reorderParts(request):
    #status bar#
    workorders = WorkOrders.objects.filter(user=request.user)
    workordercount = workorders.filter(status='OPEN').count()
    workordercountclosed = workorders.filter(status='COMPLETED').count()

    order = Parts.objects.filter(user=request.user)
    orderpending = order.filter(recieve_part=False).count()
    reorderparts = ReorderItems.objects.filter(
        user=request.user, reorder_level__gte=F('quantity')).count()

    #status bar#

    queryset = ReorderItems.objects.filter(user=request.user)

    filter = reOrderFilter(request.GET, queryset=queryset)
    queryset = filter.qs

    context = {

        "workordercount": workordercount,
        "workordercountclosed": workordercountclosed,
        "orderpending": orderpending,
        "reorderparts": reorderparts,
        "queryset": queryset,
        "filter": filter
    }

    return render(request, 'OrdersFolder/reorderParts.html', context)


@login_required(login_url='signin')
def InterimOrder(request):

    #statuc bar#
    workqueryset = WorkOrders.objects.filter(user=request.user)
    workordercount = workqueryset.filter(status='OPEN').count()
    workordercountclosed = workqueryset.filter(status='COMPLETED').count()

    order = Parts.objects.filter(user=request.user)
    orderpending = order.filter(recieve_part=False).count()

    reorderparts = Parts.objects.filter(
        user=request.user, reorder_level__gte=F('quantity')).count()

    #statuc bar#

    context = {

        "workordercountclosed": workordercountclosed,
        "workordercount": workordercount,
        "orderpending": orderpending,
        "reorderparts": reorderparts,
    }

    return render(request, "PartsFolder/interim-order.html", context)


@login_required(login_url='signin')
def recieveorder(request, pk):

    part = Parts.objects.get(user=request.user, id=pk)

    pt = part.id
    time_received = timezone.now()

    if part.part_type == 'Rotable' or part.part_type == 'Tires':
        receiveForm = RecieveOrder(pt, instance=part)
    elif part.part_type == 'Consumables' or part.part_type == 'Shelf-life':
        receiveForm = RecieveconsumShelf(pt, instance=part)
    else:
        receiveForm = RecieveAgs(pt, instance=part)

    if request.method == 'POST':
        if part.part_type == 'Rotable' or part.part_type == 'Tires':
            receiveForm = RecieveOrder(pt,
                                       request.POST, request.FILES, instance=part)
            part.receive_quantity = part.order_quantity
            part.save(update_fields=['receive_quantity'])

        elif part.part_type == 'Consumables' or part.part_type == 'Shelf-life':
            receiveForm = RecieveconsumShelf(pt,
                                             request.POST, request.FILES, instance=part)
        else:
            receiveForm = RecieveAgs(pt,
                                     request.POST, request.FILES, instance=part)

        if receiveForm.is_valid():

            if part.condition == 'REPAIRABLE' or part.condition == 'DAMAGED' or part.condition == 'INCORRECT-DOC' or part.condition == 'WRONG-PART':
                part.Quarentine = True
                part.save(update_fields=['Quarentine'])
                part.recieve_part = True
                part.save(update_fields=['recieve_part'])

            else:
                part.condition = 'NEW'
                part.save(update_fields=['condition'])

            if part.receive_quantity == part.order_quantity:

                part.ticketed = False
                part.save(update_fields=['ticketed'])

                quantity = part.order_quantity
                part.quantity += quantity
                part.save(update_fields=['quantity'])

                part.order_quantity = 0
                part.save(update_fields=['order_quantity'])
                part.date_received = timezone.now()

                receiveForm.save()  # save the form into the database

                if part.Quarentine == False:
                    if request.is_ajax():
                        if part.tail_number.name == "Stock":
                            return JsonResponse({'success': 'Adding Part to Stock Database...', 'redirect_to': reverse('instructions', kwargs={'pk': part.id})})
                        else:
                            return JsonResponse({'success': 'Adding Part to Reserved Stock Database...', 'redirect_to': reverse('instructions', kwargs={'pk': part.id})})
                    # return redirect('instructions', pk=part.id)
                else:
                    if request.is_ajax():
                        return JsonResponse({'success': 'Adding Part to Quarentine Database...', 'redirect_to': reverse('orderpart')})
                    # return redirect('orderpart')

            else:
                qtyleftOver = 0
                part.ticketed = False
                part.save(update_fields=['ticketed'])

                qtyleftOver = part.order_quantity - part.receive_quantity
                part.quantity = part.receive_quantity
                part.save(update_fields=['quantity'])

                part.order_quantity = 0
                part.save(update_fields=['order_quantity'])
                part.date_received = timezone.now()

                receiveForm.save()  # save the form into the database

                p = Parts(description=part.description,
                          part_number=part.part_number,
                          order_quantity=qtyleftOver,
                          ipc_reference=part.ipc_reference,
                          date_ordered=part.date_ordered,
                          vendor=part.vendor,
                          tail_number=part.tail_number,
                          ordered_by=part.ordered_by,
                          part_type=part.part_type,
                          Historical=False,
                          user=request.user)
                p.save()

                if part.Quarentine == False:
                    if request.is_ajax():
                        if part.tail_number.name == "Stock":
                            return JsonResponse({'success': 'Adding Part to Stock Database...', 'redirect_to': reverse('instructions', kwargs={'pk': part.id})})
                        else:
                            return JsonResponse({'success': 'Adding Part to Reserved Stock Database...', 'redirect_to': reverse('instructions', kwargs={'pk': part.id})})
                    else:
                        if request.is_ajax():
                            return JsonResponse({'success': 'Adding Part to Quarentine Database...', 'redirect_to': reverse('orderpart')})
                        # return redirect('orderpart')

    context = {'receiveForm': receiveForm,
               "part": part, 'time': time_received, }
    if request.is_ajax():
        return JsonResponse({'error': True})

    return render(request, "OrdersFolder/recieveorder.html", context)


@login_required(login_url='signin')
def instructions(request, pk):
    reorderExist = False
    check = False
    label = ""
    listPart = []
    dictPartNumbers = {}
    # obtain the specific the part link
    part = Parts.objects.get(user=request.user, id=pk)

    catagory = part.part_type

    # create a list of unique part numbers pertaining to a certain catagory.
    PartNumberList = []
    querysetPartList = Parts.objects.filter(
        user=request.user, recieve_part=True, part_type=catagory, Quarentine=False)

    for x in querysetPartList:
        PartNumberList.append(x.part_number)

    # Below is representation of unqiue p# list for a specifc catagory
    PartNumberList = sorted(set(PartNumberList))

    listPart = PlaceNewPartNumber(part.part_number, PartNumberList)

    part.recieve_part = True
    part.save(update_fields=['recieve_part'])

    if part.part_type != 'Consumables' and part.tail_number.name == 'Stock':
        part.bin_number = listPart[1]
        part.save(update_fields=['bin_number'])
    else:
        pass

    if listPart[0] == True:
        label = listPart[1]
        check = True
    else:
        label = listPart[1]

    quersetReOrder = ReorderItems.objects.all()
    if part.tail_number.name == 'Stock':
        for x in quersetReOrder:
            if x.part_number == part.part_number:
                x.quantity = x.quantity + part.quantity
                x.save(update_fields=['quantity'])
                reorderExist = True
                break
            else:
                pass

    if not reorderExist:
        if part.tail_number.name == 'Stock':
            reOrderParts = ReorderItems(part_type=part.part_type,
                                        description=part.description,
                                        part_number=part.part_number,
                                        ipc_reference=part.ipc_reference,
                                        tail_number=part.tail_number,
                                        date_ordered=timezone.now(),
                                        quantity=part.quantity,
                                        price=part.price,
                                        user=request.user
                                        )
            reOrderParts.save()

    else:
        pass

    context = {'part': part, 'label': label, 'check': check}
    return render(request, 'OrdersFolder/recieveInstructions.html', context)


@login_required(login_url='signin')
def exportorder(request):

    queryset = Parts.objects.filter(
        user=request.user, recieve_part=False).order_by('date_ordered').reverse()

    myFilter_order = CreateOrderFilter(request.GET, queryset=queryset)
    queryset = myFilter_order.qs

    context = {"queryset": queryset, "myfilter": myFilter_order, }
    return render(request, "OrdersFolder/exportorders.html", context)


@login_required(login_url='signin')
def exportstatus(request, pk):

    queryset_specific = Parts.objects.get(user=request.user, id=pk)
    queryset_specific.ticketed = True

    queryset_specific.save(update_fields=['ticketed'])
    return redirect('exportorder')


@login_required(login_url='signin')
def exportstatusdel(request, pk):
    queryset_specific = Parts.objects.get(user=request.user, id=pk)
    queryset_specific.ticketed = False

    queryset_specific.save(update_fields=['ticketed'])
    return redirect('exportorder')
#-----------------------------------------#

#Tool Logic-------------------------------#


@login_required(login_url='signin')
def tools(request):
    condition = False
    Check = 0
    queryset = Tools_Calibrated.objects.filter(user=request.user)
    querysetUncali = Tools_UnCalibrated.objects.filter(user=request.user)

    #statuc bar#
    workqueryset = WorkOrders.objects.filter(user=request.user)
    workordercount = workqueryset.filter(status='OPEN').count()
    workordercountclosed = workqueryset.filter(status='COMPLETED').count()

    order = Parts.objects.filter(user=request.user)
    orderpending = order.filter(recieve_part=False).count()
    reorderparts = ReorderItems.objects.filter(
        user=request.user, reorder_level__gte=F('quantity')).count()

    #statuc bar#

    #calibrated Tools---------#
    Calibratedqueryset = queryset.filter(
        calibrated=True, issued=False).order_by('expiry_date')

    #-------------------------------------#

    #Uncalibrated Tools---------#
    Uncalibratedqueryset = querysetUncali.filter(issued=False)
    #-------------------------------------#

    #Tools needed to be calibrated---------#
    Uncalibratedcalibtrated = queryset.filter(calibrated=False)
    #-------------------------------------#

    #Send to Calibration--------------------#

    #---------------------------------------#

    #forms---------------------------------#
    form = ChooseToolType(request.POST or None, request.FILES or None)
    form.instance.user = request.user
    displayform = ""

    if request.method == 'POST':

        if 'tool_type' in request.POST.keys():

            if request.POST['tool_type'] == '0':
                displayform = CalibratedToolForm(condition,
                                                 request.POST or None)
                displayform.instance.user = request.user
                Check = 1
                if form.is_valid():
                    form.save()

            elif request.POST['tool_type'] == '1':
                displayform = UnCalibratedToolForm(
                    request.POST or None)
                displayform.instance.user = request.user
                Check = 0
                if form.is_valid():
                    form.save()

        if "Save" in request.POST:

            field_name = 'tool_type'
            obj = ToolChecker.objects.last()
            field_value = getattr(obj, field_name)

            if field_value == 0:
                displayform = CalibratedToolForm(condition,
                                                 request.POST, request.FILES)
                displayform.instance.user = request.user
                if displayform.is_valid():
                    task = displayform.save()

                    objdel = ToolChecker.objects.all()
                    objdel.delete()
                    return redirect('toolinstructions', pk=task.id)

            if field_value == 1:
                displayform = UnCalibratedToolForm(
                    request.POST or None)
                displayform.instance.user = request.user
                if displayform.is_valid():
                    displayform.save()
                    objdel = ToolChecker.objects.all()
                    objdel.delete()
                    return redirect('tools')

    else:
        displayform = ""
    #--------------------------------------#

    #Filters----------------------#
    CaliFilter = CalibratedFilter(
        request.GET, queryset=Calibratedqueryset)
    Calibratedqueryset = CaliFilter.qs

    UnCaliFilter = UnCalibratedFilter(
        request.GET, queryset=Uncalibratedqueryset)
    Uncalibratedqueryset = UnCaliFilter.qs

    CaliUnCali = CalibratedFilter(
        request.GET, queryset=Uncalibratedcalibtrated)
    Uncalibratedcalibtrated = CaliUnCali.qs
    #----------------------------#

    context = {
        "workordercountclosed": workordercountclosed,
        "workordercount": workordercount,
        "Cali": Calibratedqueryset,
        "UnCali": Uncalibratedqueryset,
        "needsCali": Uncalibratedcalibtrated,
        "CalibratedFilter": CalibratedFilter,
        "UnCaliFilter": UnCaliFilter,
        "CaliUnCali": CaliUnCali,
        "form": form,
        "displayform": displayform,
        "orderpending": orderpending,
        "reorderparts": reorderparts,
        "Check": Check,
    }

    return render(request, "ToolsFolder/tools.html", context)


@login_required(login_url='signin')
def toolinstructions(request, pk):
    tools = Tools_Calibrated.objects.get(user=request.user, id=pk)

    context = {"tools": tools}
    return render(request, "ToolsFolder/toolinstructions.html", context)


@login_required(login_url='signin')
def change_calibration_status(request, pk):
    tool_specific = Tools_Calibrated.objects.get(user=request.user, id=pk)
    tool_specific.calibrated = False

    tool_specific.save(update_fields=['calibrated'])

    return redirect('tools')


@login_required(login_url='signin')
def deleteUnCali(request, pk):
    queryset = Tools_UnCalibrated.objects.get(user=request.user, id=pk)
    queryset.delete()
    return redirect('tools')


@login_required(login_url='signin')
def deleteCali(request, pk):
    queryset = Tools_Calibrated.objects.get(user=request.user, id=pk)
    queryset.delete()
    return redirect('tools')


@login_required(login_url='signin')
def editCali(request, pk):
    condition = True
    calitool = Tools_Calibrated.objects.get(user=request.user, id=pk)
    formCali = CalibratedToolForm(condition, instance=calitool)

    if request.method == 'POST':
        # senidng new data into a pre exisitng field.
        formCali = CalibratedToolForm(
            condition, request.POST, instance=calitool)
        if formCali.is_valid():
            formCali.save()  # save the form into the database
            return redirect('tools')  # redirect to home page

    context = {'formCali': formCali}
    return render(request, 'ToolsFolder/editCali.html', context)


@login_required(login_url='signin')
def editUnCali(request, pk):

    UnCaliTool = Tools_UnCalibrated.objects.get(user=request.user, id=pk)
    UnCaliform = UnCalibratedToolForm(instance=UnCaliTool)

    if request.method == 'POST':
        # senidng new data into a pre exisitng field.
        UnCaliform = UnCalibratedToolForm(
            request.POST, instance=UnCaliTool)
        if UnCaliform.is_valid():
            UnCaliform.save()  # save the form into the database
            return redirect('tools')  # redirect to home page

    context = {'UnCaliform': UnCaliform}
    return render(request, 'ToolsFolder/editUnCali.html', context)


@login_required(login_url='signin')
def issueworkorderCali(request, pk):

    calitool = Tools_Calibrated.objects.get(user=request.user, id=pk)
    formissueCali = CreateWorkOrderFormCali(instance=calitool)

    if request.method == 'POST':
        if "CancelIssue" in request.POST:
            return redirect('tools')

        formissueCali = CreateWorkOrderFormCali(
            request.POST, instance=calitool)
        if formissueCali.is_valid():
            if "SaveIssue" in request.POST:
                calitool.issued = True
                calitool.save(update_fields=['issued'])
                formissueCali.save()
                return redirect('tools')

    context = {'formissueCali': formissueCali, "calitool": calitool}
    return render(request, 'ToolsFolder/issueworkorderCali.html', context)


@login_required(login_url='signin')
def issueUnCali(request, pk):

    Uncalitool = Tools_UnCalibrated.objects.get(user=request.user, id=pk)
    formissueUnCali = CreateWorkOrderFormUnCali(instance=Uncalitool)

    if request.method == 'POST':

        if "CancelIssue" in request.POST:
            return redirect('tools')
        # senidng new data into a pre exisitng field.
        formissueUnCali = CreateWorkOrderFormUnCali(
            request.POST, instance=Uncalitool)
        if formissueUnCali.is_valid():
            if "SaveIssue" in request.POST:
                Uncalitool.issued = True
                Uncalitool.save(update_fields=['issued'])
                Uncalitool.save()  # save the form into the database
                return redirect('tools')  # redirect to home page

    context = {'formissueUnCali': formissueUnCali,
               'Uncalitool': Uncalitool}
    return render(request, 'ToolsFolder/issueUncali.html', context)


@login_required(login_url='signin')
def calicomplete(request, pk):

    calitool = Tools_Calibrated.objects.get(user=request.user, id=pk)
    formCaliComp = CompleteCalibrationForm(
        request.POST, request.FILES, instance=calitool)

    if request.method == 'POST':
        # senidng new data into a pre exisitng field.
        # formCaliComp = CompleteCalibrationForm(
        #     request.POST, request.FILES, instance=calitool)
        if formCaliComp.is_valid():
            formCaliComp.save()
            calitool.calibrated = True
            calitool.save(update_fields=['calibrated'])
            return redirect('tools')  # redirect to home page

    context = {'formCaliComp': formCaliComp, "calitool": calitool}
    return render(request, 'ToolsFolder/calibrationcomplete.html', context)
#-----------------------------------------#

#Exporting Logic---------------------------#

#Excel ------------------------#


@login_required(login_url='signin')
def exportXlsxCali(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Calibrated_Tools.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Calibration-Tools')

    row_num = 2

    font_style = xlwt.XFStyle()
    font_size = xlwt.XFStyle()

    font_size.font.size = 28
    font_size.font.bold = True

    font_style.font.bold = True
    ws.write(0, 0, 'Calibrated Tools', font_size)

    columns = ['Description', 'Part-Number', 'Serial-Number', 'Date-Recieved',
               'Date-Calibrated', 'Expiry-Date', 'Cert-No', 'Range']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Tools_Calibrated.objects.filter(user=request.user, calibrated=True, issued=False).values_list(
        'description', 'part_number', 'serial_number', 'recieved', 'calibrated_date', 'expiry_date', 'cert_no', 'range_no')

    for row in rows:

        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)
    return response


@login_required(login_url='signin')
def exportXlsxUnCali(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="UnCalibrated_Tools.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('UnCalibration-Tools')

    row_num = 2

    font_style = xlwt.XFStyle()
    font_size = xlwt.XFStyle()

    font_size.font.size = 28
    font_size.font.bold = True

    font_style.font.bold = True
    ws.write(0, 0, 'UnCalibrated Tools', font_size)

    columns = ['Description', 'Part-Number', 'Serial-Number', 'Date-Recieved'
               ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Tools_UnCalibrated.objects.filter(user=request.user, issued=False).values_list(
        'description', 'part_number', 'serial_number', 'recieved')

    for row in rows:

        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)
    return response


@login_required(login_url='signin')
def exportXlsInventory(request, Type):
    name = ""
    namefile = ""
    columns = []

    if Type == 'Stock':
        name = 'Stock Inventory'
        namefile = 'attachment; filename="StockInventory.xls"'
        rows = []
        listx = []
        queryset = Parts.objects.filter(user=request.user, tail_number='Stock', Historical=False,
                                        recieve_part=True).order_by('date_received').reverse()

        rows = queryset.values_list('description', 'part_number', 'part_type', 'batch_no',
                                    'serial_number', 'bin_number', 'quantity', 'inspector', 'condition')

        columns = ['Description', 'Part #', 'Part-Type', 'S#/B#/L#', 'Bin #', 'Quantity', 'Inspector', 'Condition'
                   ]
        tups = []

        for check in rows:

            if check[2] == 'Rotable' or check[2] == 'Tires':
                listx = list(check)
                listx[3] = listx[4]
                del listx[4]
                tups += listx

            else:
                listx = list(check)
                del listx[4]
                tups += listx

        # lst = [50,"Python","JournalDev",100]
        lst_tuple = [x for x in zip(*[iter(tups)]*8)]

    if Type == "Reserved":
        name = 'Reserved Inventory'
        namefile = 'attachment; filename="ReservedInventory.xls"'
        queryset = Parts.objects.filter(user=request.user, tail_number__startswith="N", Historical=False,
                                        recieve_part=True).order_by('date_received').reverse()
        rows = queryset.values_list('description', 'part_type', 'tail_number', 'part_number',
                                    'batch_no', 'serial_number', 'quantity', 'inspector', 'condition')
        columns = ['Description', 'Part-Type', 'Reserved For:', 'Part #',
                   'S#/B#/L#', 'Quantity', 'Inspector', 'Condition']

        tups = []
        for check in rows:

            if check[1] == 'Rotable' or check[1] == 'Tires':
                listx = list(check)
                listx[4] = listx[5]
                del listx[5]
                tups += listx

            else:
                listx = list(check)
                del listx[5]
                tups += listx

        # lst = [50,"Python","JournalDev",100]
    lst_tuple = [x for x in zip(*[iter(tups)]*8)]

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = namefile

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet(name)

    row_num = 2

    font_style = xlwt.XFStyle()
    font_size = xlwt.XFStyle()

    font_size.font.size = 28
    font_size.font.bold = True
    font_style.font.bold = True

    ws.write(0, 0, name, font_size)
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()

    for row in lst_tuple:

        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(
                row[col_num]), font_style)

    wb.save(response)
    return response
#---------------------------------#

#Pdf-----------------------------#


@login_required(login_url='signin')
def exportPDForder(request):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; file="Orders.pdf"'

    response['Content-Transfer-Encoding'] = 'binary'

    queryset = Parts.objects.filter(user=request.user, ticketed=True)
    for q in queryset:
        q.exported = True
        q.save(update_fields=['exported'])

    date = timezone.now()
    html_string = render_to_string(
        'PDFFolder/pdfoutput.html', {'orders': queryset, 'total': queryset.count(), "date": date})
    html = HTML(string=html_string)
    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, 'rb')
        response.write(output.read())

    return response


@login_required(login_url='signin')
def exportPDFWorkorder(request, pk):
    total = 0

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; file="Work-Orders.pdf"'

    response['Content-Transfer-Encoding'] = 'binary'

    workorder_specific = WorkOrders.objects.get(user=request.user, id=pk)
    querysetDisplay = WorkOrders.objects.get(user=request.user, id=pk)

    # return all parts related to work id
    partsIssue = workorder_specific.partworkorders_set.filter(
        receivedRepair=False).order_by('created_at').reverse()

    partsReceived = workorder_specific.partworkorders_set.filter(
        receivedRepair=True).order_by('created_at').reverse()

    # Display Total
    for parts in partsIssue:
        total += parts.price * parts.issue_quantity

    # Displaying the workorder we are linking too
    workordernumber = workorder_specific.workorder_number

    date = timezone.now()
    html_string = render_to_string('PDFFolder/pdfoutputWorkorders.html',
                                   {'partsIssue': partsIssue, 'partsReceived': partsReceived,
                                    'querysetDisplay': querysetDisplay, "total": total, "date": date})
    html = HTML(string=html_string)
    result = html.write_pdf()

    # f1 = result

    #         f2 =

    #         # Into a PDF file objects
    #         pdfFileObj1 = PyPDF2.PdfFileReader(f1)
    #         pdfFileObj2 = PyPDF2.PdfFileReader(f2)

    #         # Create a PDF file merge objects, add merge files
    #         pdfMerger = PyPDF2.PdfFileMerger()
    #         pdfMerger.append(pdfFileObj1)
    #         pdfMerger.append(pdfFileObj2)

    #         # Merge file object is written to merged_file.pdf
    #         with open('merged_file.pdf', 'wb') as pdfOutputFile:
    #             pdfMerger.write(pdfOutputFile)

    #         # Open merger merged_file.pdf, by HttpResponse output
    #         with open('merged_file.pdf', 'rb') as merged_file:
    #             response = HttpResponse(merged_file.read(), content_type='application/pdf')
    #             response['Content-Disposition'] = 'attachment; filename="merged_file.pdf"'
    #             return response

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, 'rb')

        response.write(output.read())

    return response
    #End exporting Logic--------------------------#


#pdf------------------------------#
#------------------------------------------#
