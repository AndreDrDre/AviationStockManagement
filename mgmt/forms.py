from django import forms
from .models import *
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q
import os


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

#-----------------------------------#


class DateInput(forms.DateInput):
    input_type = 'date'


class AddShoppingItem(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ['description', 'part_number',
                  'quantity', 're_orderLevel', 'unitPrice']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'required': True},),
            'quantity': forms.TextInput(attrs={'class': 'form-control', 'required': True},),
            'part_number': forms.TextInput(attrs={'class': 'form-control', 'required': False},),
            're_orderLevel': forms.TextInput(attrs={'class': 'form-control', 'required': True},),
            'unitPrice': forms.NumberInput(attrs={'class': 'form-control', 'required': True, 'step': 0.01},),
        }


class OrderMoreForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ['order_quantity', "unitPrice", "ordered_by", "From"]
        widgets = {
            'order_quantity': forms.NumberInput(attrs={'class': 'form-control', 'required': True},),
            'unitPrice': forms.NumberInput(attrs={'class': 'form-control', 'required': True},),
            'ordered_by': forms.Select(attrs={'class': 'form-control', 'required': True},),
            'From': forms.TextInput(attrs={'class': 'form-control', 'required': True},),

        }

    def clean_order_quantity(self):
        data = self.cleaned_data['order_quantity']
        if data == 0 or data < 0:
            raise ValidationError(
                "You cannot Order zero quantity or less than zero quantity!")
        else:
            return data
        return data


class issueShopForm(forms.ModelForm):

    class Meta:
        model = ShoppingList
        fields = ['issue_quantity']
        widgets = {
            'issue_quantity': forms.NumberInput(attrs={'class': 'form-control', 'required': True},),

        }

    def clean_issue_quantity(self):
        data = self.cleaned_data['issue_quantity']
        if data == 0 or data < 0:
            raise ValidationError(
                "You cannot issue zero quantity or less than zero quantity!")
        elif self.instance.quantity < data:
            raise ValidationError(
                "You cannot issue out more than the avaliable amount!")
        else:
            return data
        return data


class ReceiveShopForm(forms.ModelForm):

    class Meta:
        model = ShoppingList
        fields = ['receive_quantity']
        widgets = {
            'receive_quantity': forms.NumberInput(attrs={'class': 'form-control', 'required': True},),

        }

    def clean_receive_quantity(self):
        data = self.cleaned_data['receive_quantity']
        if data == 0 or data < 0:
            raise ValidationError(
                "You cannot receive zero quantity or less than zero quantity!")
        elif self.instance.order_quantity < data:
            raise ValidationError(
                "You cannot receive more than the ordered amount!")
        else:
            return data
        return data


#-----------------------------------#


class PartBinForm(forms.Form):

    bin_number = forms.CharField(max_length=50, required=False)

    def __init__(self, *args, **kwargs):
        super(PartBinForm, self).__init__(*args, **kwargs)
        self.fields['bin_number'].label = "Bin Number:"


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username',  'password1', 'password2']


#Store Forms------------------------------#


class EditPartForm(forms.ModelForm):
    class Meta:
        model = Parts
        fields = ['description', 'part_number', 'serial_number',
                  'ipc_reference', 'invoice_number', 'purchase_order_number', 'bin_number', 'cert_document']

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
    cert_document = forms.FileField(required=False)

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
        fields = ['tail_number',
                  'ldgs_at_open', 'hours_at_open', 'workorder_number', ]

        widgets = {
            'tail_number': forms.Select(attrs={'class': 'form-control', 'required': True, }),
            'ldgs_at_open': forms.TextInput(attrs={'class': 'form-control', 'required': True, }),
            'hours_at_open': forms.TextInput(attrs={'class': 'form-control', 'required': True, }),
            'workorder_number': forms.TextInput(attrs={'class': 'form-control', 'required': True, }),

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
        label='Tail # ', queryset=TailNumber.objects.all(), required=True)
    orderQTY = forms.IntegerField(label='Order quantity', required=True)

    def __init__(self, *args, **kwargs):
        super(ReOrderForm, self).__init__(*args, **kwargs)

        self.fields['orderQTY'].label = "Order Qty:"


class CreateOrder(forms.Form):

    part_type = forms.ChoiceField(choices=PARTTYPE_CHOICES, required=True)
    description = forms.CharField(max_length=100, required=True)
    part_number = forms.CharField(max_length=50, required=True)
    ipc_reference = forms.CharField(max_length=200)

    order_quantity = forms.IntegerField(label='Order quantity', required=True)

    tail_number = forms.ModelChoiceField(label='Tail #',
                                         queryset=TailNumber.objects.all(), required=True)
    ordered_by = forms.ModelChoiceField(label='Ordered by',
                                        queryset=Employees.objects.all(), required=True)


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
                                         queryset=TailNumber.objects.filter(~Q(name='Stock')), required=True)
    part_type = forms.ChoiceField(choices=PARTTYPE_CHOICES, required=True)
    description = forms.CharField(max_length=100, required=True)
    part_number = forms.CharField(max_length=50, label='Part #', required=True)
    indentifier = forms.CharField(max_length=50, label="S#/B#", required=True)
    vendor = forms.CharField(max_length=200)

    # Receive-Part
    order_quantity = forms.IntegerField(label="Quantity", required=True)
    invoice_number = forms.CharField(label="Invoice No.", required=False)
    purchase_order_number = forms.CharField(
        label="Purchase Order No.", required=False)
    cert_document = forms.FileField(required=False)

    inspector = forms.ModelChoiceField(label='Inspector',
                                       queryset=Employees.objects.all(), required=True)

    condition = forms.ChoiceField(
        choices=CONDITIONS_CHOICES)

    workorder = forms.ModelChoiceField(label='Inspector',
                                       queryset=WorkOrders.objects.filter(status='OPEN'), required=True)

    jobCardNumber = forms.CharField(
        max_length=100, label="Work Card #", required=True)
    price = forms.IntegerField(label="Price", required=False)

    expiry_date = forms.DateField(
        widget=DateInput(), required=False
    )

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
            del self.fields['purchase_order_number']
            del self.fields['invoice_number']
            del self.fields['vendor']
            del self.fields['order_quantity']
            del self.fields['expiry_date']
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

    part_type = forms.ChoiceField(choices=PARTTYPE_CHOICES, required=True)
    description = forms.CharField(max_length=100, required=True)
    part_number = forms.CharField(max_length=50, label='Part #', required=True)
    indentifier = forms.CharField(max_length=50, label="S#/B#", required=True)
    # Receive-Part
    order_quantity = forms.IntegerField(label="Quantity", required=True)
    # cert_document = forms.ImageField(
    #     label='Certification Document', required=False)
    cert_document = forms.FileField(required=False)

    inspector = forms.ModelChoiceField(label='Inspector',
                                       queryset=Employees.objects.all(), required=True)
    condition = forms.ChoiceField(
        choices=CONDITIONS_CHOICES, required=True)

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

            'inspector': forms.Select(attrs={'class': 'form-control', "required": True}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control', "required": True}),
            'vendor': forms.TextInput(attrs={'class': 'form-control', "required": True}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control', "required": True}),
            'purchase_order_number': forms.TextInput(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control', "required": True}),
        }

    cert_document = forms.FileField(required=False)

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
            'receive_quantity': forms.TextInput(attrs={'class': 'form-control', "required": True}),
            'inspector': forms.Select(attrs={'class': 'form-control', "required": True}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control', "required": True}),
            'batch_no': forms.TextInput(attrs={'class': 'form-control', "required": True}),
            'purchase_order_number': forms.TextInput(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control', "required": True}),
        }
    cert_document = forms.FileField(required=False)

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
            'receive_quantity': forms.TextInput(attrs={'class': 'form-control', "required": True}),
            'inspector': forms.Select(attrs={'class': 'form-control', "required": True}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control', "required": True}),
            'batch_no': forms.TextInput(attrs={'class': 'form-control', "required": True}),
            'purchase_order_number': forms.TextInput(attrs={'class': 'form-control', }),
            'expiry_date': DateInput(),
            'condition': forms.Select(attrs={'class': 'form-control', "required": True}),

        }

    cert_document = forms.FileField(required=False)

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

            'order_quantity': forms.TextInput(attrs={'class': 'form-control', "required": True}),
            'ordered_by': forms.Select(attrs={'class': 'form-control', "required": True}),
            'vendor': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_order_number': forms.TextInput(attrs={'class': 'form-control'}),
        }


class RepairForm(forms.ModelForm):
    class Meta:
        model = Parts
        fields = ['repaired_by', ]
        widgets = {

            'repaired_by': forms.Select(attrs={'class': 'form-control', "required": True}),

        }


class shippingInfoForm(forms.ModelForm):
    class Meta:
        model = Parts
        fields = ['length', 'breadth', 'height', 'weight']
        widgets = {
            'length': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'length in inches'}),
            'breadth': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'breadth in inches'}),
            'height': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'height in inches'}),
            'weight': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'weight in pounds'}),
        }


class repairReturnForm(forms.ModelForm):
    class Meta:
        model = Parts
        fields = ['inspector', 'cert_document', 'price']

    cert_document = forms.FileField(required=True)

    def clean_cert_document(self):
        data = self.cleaned_data['cert_document']
        if data == None:
            raise ValidationError(
                "You need to supply a Serviceable Tag to release this part!")

        else:
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
                part=self.instance, cert_document=self.instance.cert_document, price=0.0, **self.cleaned_data)

        else:

            PartWorkOrders.objects.create(
                part=self.instance, cert_document=self.instance.cert_document, price=self.instance.price, **self.cleaned_data)

    def clean_issue_quantity(self):

        data = self.cleaned_data['issue_quantity']

        if (data > self.instance.quantity):
            raise ValidationError(
                "You cannot issue more than the avaliable quantity!")
        elif data == 0:
            raise ValidationError(
                "You cannot issue 0 Parts!")
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
            'description': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'part_number': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'calibrated_date': DateInput(),
            'expiry_date': DateInput(),
            'range_no': forms.TextInput(attrs={'class': 'form-control', 'required': True}),


        }

    calibration_certificate = forms.FileField(required=False)

    def clean_calibration_certificate(self):
        uploaded_file = self.cleaned_data['calibration_certificate']
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

    def __init__(self, condition, *args, **kwargs):
        super(CalibratedToolForm, self).__init__(*args, **kwargs)
        self.fields['calibration_certificate'].label = "Calibration Certificate"
        if condition:
            del self.fields['calibration_certificate']


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

    class Meta:
        model = Tools_Calibrated
        fields = ['workorder_no', 'issuedby', 'jobcard']
        widgets = {
            'workorder_no': forms.Select(attrs={'class': 'form-control', 'required': True, }),
            'issuedby': forms.Select(attrs={'class': 'form-control', 'required': True, }),
            'jobcard': forms.TextInput(attrs={'class': 'form-control', 'required': True, }),
        }

    def clean_workorder_no(self):

        data = self.cleaned_data['workorder_no']

        if (data == self.instance.workorder_no):
            raise ValidationError(
                "You cannot move this tool to same work-order it is currently in!")
        else:
            return data
        return data


class CreateWorkOrderFormUnCali(forms.ModelForm):

    class Meta:
        model = Tools_UnCalibrated

        fields = ['workorder_no']
        widgets = {
            'workorder_no': forms.Select(attrs={'class': 'form-control', 'required': True, }),

        }

    def clean_workorder_no(self):

        data = self.cleaned_data['workorder_no']

        if (data == self.instance.workorder_no):
            raise ValidationError(
                "You cannot move this tool to same work-order it is currently in!")
        else:
            return data
        return data


class CompleteCalibrationForm(forms.ModelForm):
    class Meta:
        model = Tools_Calibrated
        fields = ['calibrated_date', 'expiry_date', 'calibration_certificate']
        widgets = {

            'calibrated_date': DateInput(),
            'expiry_date': DateInput(),

        }
    calibration_certificate = forms.FileField(required=True)

    def clean_calibration_certificate(self):

        data = self.cleaned_data['calibration_certificate']
        if data == None:
            raise ValidationError(
                "You need to supply a calibration certificate for this Tool!")

        else:

            uploaded_file = self.cleaned_data['calibration_certificate']
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

    def __init__(self, *args, **kwargs):
        super(CompleteCalibrationForm, self).__init__(*args, **kwargs)

    def clean_expiry_date(self):
        data = self.cleaned_data['expiry_date']
        if data == None:
            raise ValidationError(
                "You need to supply an expiry date for this Tool!")
        else:
            return data
        return data

    def clean_calibrated_date(self):
        data = self.cleaned_data['calibrated_date']
        if data == None:
            raise ValidationError(
                "You need to supply a calibration date for this Tool!")
        else:
            return data
        return data

#End Tool Forms------------------------------------------------------#
