from django import forms
from .models import *
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q


PARTTYPE_CHOICES = (
    ("Rotable", "Rotable"),
    ("Tires", "Tires"),
    ("AGS", "AGS"),
    ("Consumables", "Consumables"),
    ("Shelf-life", "Shelf-life"),

)

CONDITIONS_CHOICES = (
    ("NEW", "NEW"),
    ("OH", "OH"),
    ("AR", "AR"),
    ("SV", "SV"),
    ("REPAIRABLE", "REPAIRABLE"),
    ("DAMAGED", "DAMAGED"),
    ("INCORRECT-DOC", "INCORRECT-DOC"),
    ("WRONG-PART", "WRONG-PART"),

)


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username',  'password1', 'password2']


class DateInput(forms.DateInput):
    input_type = 'date'

#Store Forms------------------------------#


class EditPartForm(forms.ModelForm):
    class Meta:
        model = Parts
        fields = ['description', 'part_number', 'serial_number',
                  'ipc_reference', 'invoice_number', 'purchase_order_number', 'bin_number']

        widgets = {
            'reorder_level': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'part_number': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_order_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bin_number': forms.TextInput(attrs={'class': 'form-control'}),
            'ipc_reference': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ReorderLevelForm(forms.ModelForm):
    class Meta:
        model = ReorderItems
        fields = ['reorder_level']
        widgets = {

            'reorder_level': forms.TextInput(attrs={'class': 'form-control'}),

        }
#------------------------------------------#

#WorkOrders---------------------------------------------------------#


class CreateWorkorder(forms.ModelForm):

    class Meta:
        # I only want to display certain fields from a model
        model = WorkOrders
        fields = ['tail_number', 'type_airframe',
                  'ldgs_at_open', 'hours_at_open', 'workorder_number', ]

        widgets = {
            'tail_number': forms.Select(attrs={'class': 'form-control'}),
            'type_airframe': forms.TextInput(attrs={'class': 'form-control'}),
            'ldgs_at_open': forms.TextInput(attrs={'class': 'form-control'}),
            'hours_at_open': forms.TextInput(attrs={'class': 'form-control'}),
            'workorder_number': forms.TextInput(attrs={'class': 'form-control'}),

        }

    def __init__(self, *args, **kwargs):
        super(CreateWorkorder, self).__init__(*args, **kwargs)
        self.fields['tail_number'] = forms.ModelChoiceField(label='Tail #',
                                                            queryset=TailNumber.objects.filter(~Q(name='Stock')))
#-------------------------------------------------------------------#

#Add parts not from an order----------------------------------------#

class ReOrderForm(forms.Form):

    ordered_by = forms.ModelChoiceField(
        label='Ordered By', queryset=Employees.objects.all(), required=True)
    tail_number = forms.ModelChoiceField(
        label='Tail #', queryset=TailNumber.objects.all(), required=True)
    orderQTY = forms.IntegerField(label='Order quantity', required=True)

    def __init__(self, *args, **kwargs):
        super(ReOrderForm, self).__init__(*args, **kwargs)

        self.fields['orderQTY'].label = "Order Qty:"

class CreateOrder(forms.Form):

    part_type = forms.ChoiceField(choices=PARTTYPE_CHOICES)
    description = forms.CharField(max_length=100)
    part_number = forms.CharField(max_length=50)
    ipc_reference = forms.CharField(max_length=200)

    order_quantity = forms.IntegerField(label='Order quantity')

    tail_number = forms.ModelChoiceField(label='Tail #',
                                         queryset=TailNumber.objects.all())
    ordered_by = forms.ModelChoiceField(label='Ordered by',
                                        queryset=Employees.objects.all())


#-------------------------------------------------------------------#

#Order Forms----------------------------------------------------------#

class waybillForm(forms.ModelForm):
    class Meta:
        model = Parts
        fields = ['waybill']
        widgets = {

            'waybill': forms.TextInput(attrs={'class': 'form-control'}),

        }

class PriceForm(forms.ModelForm):
    class Meta:
        model = Parts
        fields = ['price']
        widgets = {
            # 'price': forms.IntegerField(label="Price"),

        }

#Consignment Inventory Form-------------------#

class AddInventory(forms.Form):

    # Order-Part
    tail_number = forms.ModelChoiceField(label='Tail #',
                                         queryset=TailNumber.objects.filter(~Q(name='Stock')))
    part_type = forms.ChoiceField(choices=PARTTYPE_CHOICES)
    description = forms.CharField(max_length=100)
    part_number = forms.CharField(max_length=50, label='Part #')
    indentifier = forms.CharField(max_length=50, label="S#/B#")

    # ipc_reference = forms.CharField(max_length=200)
    vendor = forms.CharField(max_length=200)

    # Receive-Part
    order_quantity = forms.IntegerField(label="Quantity")
    # cert_document = forms.ImageField(
    #     label='Certification Document', required=False)
    cert_document = forms.FileField(required=False)

    inspector = forms.ModelChoiceField(label='Inspector',
                                       queryset=Employees.objects.all(), required=True)

    condition = forms.ChoiceField(
        choices=CONDITIONS_CHOICES)

    workorder = forms.ModelChoiceField(
        queryset=WorkOrders.objects.filter(status='OPEN'), required=True)

    jobCardNumber = forms.CharField(
        max_length=100, label="Work Card #", required=True)
    price = forms.IntegerField(label="Price", required=False)

    

    def clean_cert_document(self):
        uploaded_file = self.cleaned_data['cert_document']
        try:
            # create an ImageField instance
            im = forms.ImageField()
            # now check if the file is a valid image
            im.to_python(uploaded_file)
        except forms.ValidationError:
            # file is not a valid image;
            # so check if it's a pdf
            name, ext = os.path.splitext(uploaded_file.name)
            if ext not in ['.pdf', '.PDF']:
                raise forms.ValidationError(
                    "Only images and PDF files allowed")
        return uploaded_file

    def clean_order_quantity(self):

        data = self.cleaned_data['order_quantity']
        pT = self.cleaned_data['part_type']

        if pT == "Rotable" or pT == "Tires":
            if (data > 1):
                raise ValidationError(
                    "This is a serialsed part, Qty must be 1!")
            else:
                return data
        return data

    def __init__(self, Type, *args, **kwargs):
        super(AddInventory, self).__init__(*args, **kwargs)
        if Type == 'Stock':
            self.fields['price'].label = "Unit Price:"
            del self.fields['tail_number']
            del self.fields['workorder']
            del self.fields['jobCardNumber']
            self.fields['condition'] = forms.ChoiceField(
                choices=CONDITIONS_CHOICES[0:4])

        if Type == "RemoveFromAircraft":

            self.fields['condition'] = forms.ChoiceField(
                choices=CONDITIONS_CHOICES[2:5])
            del self.fields['price']
            del self.fields['vendor']
            del self.fields['order_quantity']
            self.fields['workorder'].label = "Work Order #"
            self.fields['tail_number'].label = "Removed from:"
            self.fields['cert_document'].label = "Condition Document:"
            self.fields['part_type'] = forms.ChoiceField(
                choices=PARTTYPE_CHOICES[0:3])

        if Type == 'Reserved':
            self.fields['price'].label = "Unit Price:"
            del self.fields['workorder']
            del self.fields['jobCardNumber']
            self.fields['condition'] = forms.ChoiceField(
                choices=CONDITIONS_CHOICES[0:4])


class addQuaretineInventory(forms.Form):
    # Order-Part

    part_type = forms.ChoiceField(choices=PARTTYPE_CHOICES)
    description = forms.CharField(max_length=100)
    part_number = forms.CharField(max_length=50, label='Part #')
    indentifier = forms.CharField(max_length=50, label="S#/B#")
    # Receive-Part
    order_quantity = forms.IntegerField(label="Quantity")
    cert_document = forms.ImageField(
        label='Certification Document', required=False)

    inspector = forms.ModelChoiceField(label='Inspector',
                                       queryset=Employees.objects.all())
    condition = forms.ChoiceField(
        choices=CONDITIONS_CHOICES)

    def clean_order_quantity(self):

        data = self.cleaned_data['order_quantity']
        pT = self.cleaned_data['part_type']

        if pT == "Rotable" or pT == "Tires":
            if (data > 1):
                raise ValidationError(
                    "This is a serialsed part, Qty must be 1!")
            else:
                return data
        return data

    def __init__(self, *args, **kwargs):
        super(addQuaretineInventory, self).__init__(*args, **kwargs)

        self.fields['condition'] = forms.ChoiceField(
            choices=CONDITIONS_CHOICES[4:8])

        self.fields['cert_document'].label = "Condition Document:"
        self.fields['part_type'] = forms.ChoiceField(
            choices=PARTTYPE_CHOICES[0:5])
#-------------------------------------------#

#When ordering a part from a supplier---------#
class RecieveOrder(forms.ModelForm):
    class Meta:
        model = Parts
        fields = ['inspector',
                  'invoice_number', 'serial_number', 'vendor', 'purchase_order_number', 'cert_document', 'condition']

        widgets = {

            'inspector': forms.Select(attrs={'class': 'form-control'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'vendor': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_order_number': forms.TextInput(attrs={'class': 'form-control'}),
            'cert_document': forms.FileInput(attrs={'class': 'form-control', 'required': False, }),
            'condition': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, pt, *args, **kwargs):
        super(RecieveOrder, self).__init__(*args, **kwargs)

        self.fields['condition'].label = "Condition"

#partial oders come through here--------------#
class RecieveAgs(forms.ModelForm):
    class Meta:
        model = Parts
        fields = ['receive_quantity', 'inspector',
                  'invoice_number', 'batch_no',  'purchase_order_number', 'cert_document', 'condition']
        widgets = {
            'receive_quantity': forms.TextInput(attrs={'class': 'form-control'}),
            'inspector': forms.Select(attrs={'class': 'form-control'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),

            'batch_no': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_order_number': forms.TextInput(attrs={'class': 'form-control'}),
            'cert_document': forms.FileInput(attrs={'class': 'form-control', 'required': False, }),
            'condition': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, pt, *args, **kwargs):
        super(RecieveAgs, self).__init__(*args, **kwargs)

    def clean_receive_quantity(self):

        orderQTY = self.instance.order_quantity
        ReceiveQTY = self.cleaned_data['receive_quantity']

        if ReceiveQTY > orderQTY:
            raise ValidationError(
                "ERROR : You cannot receive more than what you ordered!")
        elif ReceiveQTY == 0 or ReceiveQTY == "":
            raise ValidationError(
                "ERROR : You cannot receive 0 of this Invenotry Item!")

        else:
            return ReceiveQTY
        return ReceiveQTY

class RecieveconsumShelf(forms.ModelForm):
    class Meta:
        model = Parts

        fields = ['receive_quantity', 'inspector', 'invoice_number', 'batch_no',
                  'purchase_order_number', 'cert_document', 'expiry_date', 'condition']
        widgets = {
            'receive_quantity': forms.TextInput(attrs={'class': 'form-control'}),
            'inspector': forms.Select(attrs={'class': 'form-control'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),

            'batch_no': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_order_number': forms.TextInput(attrs={'class': 'form-control'}),
            'cert_document': forms.FileInput(attrs={'class': 'form-control', 'required': False, }),
            'expiry_date': DateInput(),
            'condition': forms.Select(attrs={'class': 'form-control'}),

        }

    def __init__(self, pt, *args, **kwargs):
        super(RecieveconsumShelf, self).__init__(*args, **kwargs)

    def clean_receive_quantity(self):

        orderQTY = self.instance.order_quantity
        ReceiveQTY = self.cleaned_data['receive_quantity']

        if ReceiveQTY > orderQTY:
            raise ValidationError(
                "ERROR : You cannot receive more than what you ordered!")
        elif ReceiveQTY == 0 or ReceiveQTY == "":
            raise ValidationError(
                "ERROR : You cannot receive 0 of this Invenotry Item!")
        else:
            return ReceiveQTY
        return ReceiveQTY

#--------------------------------------------#

#--------------------------------------------#
class CreateNewOrder(forms.ModelForm):
    class Meta:
        model = Parts
        fields = ['order_quantity', 'ordered_by',
                  'vendor', 'purchase_order_number']
        widgets = {

            'order_quantity': forms.TextInput(attrs={'class': 'form-control'}),
            'ordered_by': forms.Select(attrs={'class': 'form-control'}),
            'vendor': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_order_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class RepairForm(forms.ModelForm):
    class Meta:
        model = Parts
        fields = ['repaired_by', ]
        widgets = {

            'repaired_by': forms.Select(attrs={'class': 'form-control'}),

        }

class repairReturnForm(forms.ModelForm):
    class Meta:
        model = Parts
        fields = ['inspector', 'cert_document', 'price']
        widgets = {
            'inspector': forms.Select(attrs={'class': 'form-control'}),
            'cert_document': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, conditionCheck, *args, **kwargs):
        super(repairReturnForm, self).__init__(*args, **kwargs)

        if conditionCheck == 'REPAIRABLE':
            self.fields['price'].label = "Cost of Repair"

        if conditionCheck == 'DAMAGED':
            self.fields['price'].label = "Cost of Repair"

        if conditionCheck == 'INCORRECT-DOC':
            del self.fields['price']

        if conditionCheck == 'WRONG-PART':
            del self.fields['price']

        self.fields['cert_document'].label = "Condition Document"

class issueWorkForm(forms.ModelForm):
    workorder = forms.ModelChoiceField(queryset=None)

    class Meta:
        model = Parts
        fields = ['workorder', 'issued_by', 'jobCardNumber', 'issue_quantity']
        widgets = {

            'workorder': forms.Select(attrs={'class': 'form-control'}),
            'issued_by': forms.Select(attrs={'class': 'form-control'}),
            'issue_quantity': forms.TextInput(attrs={'class': 'form-control'}),
            'jobCardNumber': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def _save_m2m(self):

        if self.instance.price == None:
            PartWorkOrders.objects.create(
                part=self.instance, price=0.0, **self.cleaned_data)

        else:

            PartWorkOrders.objects.create(
                part=self.instance, price=self.instance.price, **self.cleaned_data)

    def clean_issue_quantity(self):

        data = self.cleaned_data['issue_quantity']

        if (data > self.instance.quantity):
            raise ValidationError(
                "You cannot issue more than the avaliable quantity!")
        else:
            return data
        return data

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(issueWorkForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['workorder'].queryset = WorkOrders.objects.filter(
                user=user, status='OPEN')
        self.fields['jobCardNumber'].label = "Work Card #"
        self.fields['workorder'].label = "Work Order #"

#Tools Forms--------------------------------------------------------#

class ChooseToolType(forms.ModelForm):
    class Meta:
        model = ToolChecker
        fields = ['tool_type', ]
        widgets = {
            'tool_type': forms.Select(attrs={'class': 'form-control'}),
        }

class CalibratedToolForm(forms.ModelForm):
    class Meta:
        model = Tools_Calibrated
        fields = ['description', 'serial_number', 'part_number',
                  'calibrated_date', 'expiry_date', 'range_no', 'calibration_certificate']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'part_number': forms.TextInput(attrs={'class': 'form-control'}),
            'calibrated_date': DateInput(),
            'expiry_date': DateInput(),
            'range_no': forms.TextInput(attrs={'class': 'form-control'}),

            'calibration_certificate': forms.FileInput(attrs={'class': 'form-control', 'required': True, }),

        }

    def __init__(self, condition, *args, **kwargs):

        super(CalibratedToolForm, self).__init__(*args, **kwargs)

        self.fields['calibration_certificate'].label = "Calibration Certificate"

        if condition:

            del self.fields['calibration_certificate']

    # def clean_calibration_certificate(self):

    #     data = self.cleaned_data['calibration_certificate']
    #     if data == None:
    #         raise ValidationError(
    #             "Please Submit a Calibration Document")

    #     else:
    #         return data

    #     return data

class UnCalibratedToolForm(forms.ModelForm):

    class Meta:
        model = Tools_UnCalibrated
        fields = ['description', 'serial_number',
                  'part_number']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'part_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CreateWorkOrderFormCali(forms.ModelForm):

    workorder_no = forms.ModelChoiceField(
        queryset=WorkOrders.objects.filter(status='OPEN'))

    class Meta:
        model = Tools_Calibrated
        fields = ['workorder_no']
        widgets = {
            'workorder_no': forms.Select(attrs={'class': 'form-control'}),

        }

class CreateWorkOrderFormUnCali(forms.ModelForm):

    workorder_no = forms.ModelChoiceField(
        queryset=WorkOrders.objects.filter(status='OPEN'))

    class Meta:
        model = Tools_UnCalibrated

        fields = ['workorder_no']
        widgets = {
            'workorder_no': forms.Select(attrs={'class': 'form-control'}),

        }

class CompleteCalibrationForm(forms.ModelForm):
    class Meta:
        model = Tools_Calibrated
        fields = ['calibrated_date', 'expiry_date', 'calibration_certificate']
        widgets = {

            'calibrated_date': DateInput(),
            'expiry_date': DateInput(),
            'calibration_certificate': forms.FileInput(attrs={'class': 'form-control', 'required': False, })

        }

    def clean_order_quantity(self):

        data = self.cleaned_data['order_quantity']
        pT = self.cleaned_data['part_type']

        if pT == "Rotable" or pT == "Tires":
            if (data > 1):
                raise ValidationError(
                    "This is a serialsed part, Qty must be 1!")
            else:
                return data
        return data

#End Tool Forms------------------------------------------------------#
   