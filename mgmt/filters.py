import django_filters
from django_filters import DateFilter
from .models import *
from django import forms
from django.db.models import Q


class WorkOrderFilter(django_filters.FilterSet):

    tail_number = django_filters.ModelChoiceFilter(
        queryset=TailNumber.objects.filter(~Q(name='Stock')))

    class Meta:
        model = WorkOrders
        fields = '__all__'
        exclude = ['type_airframe', 'ldgs_at_open', "date_added",
                   'status', 'hours_at_open', 'date_closed', 'user', 'description']

    def __init__(self, *args, **kwargs):
        super(WorkOrderFilter, self).__init__(*args, **kwargs)
        self.filters['workorder_number'].label = 'Work-Order #'


class shoppingListFilter(django_filters.FilterSet):
    class Meta:
        model = ShoppingList
        fields = ['description', 'ordered_by', ]


class CreateOrderFilter(django_filters.FilterSet):
    class Meta:
        model = Parts
        fields = ['description', 'part_number', 'ordered_by']


class CalibratedFilter(django_filters.FilterSet):
    class Meta:
        model = Tools_Calibrated
        fields = ['description', 'part_number', 'cert_no']

    def __init__(self, *args, **kwargs):
        super(CalibratedFilter, self).__init__(*args, **kwargs)
        self.filters['part_number'].label = 'Part #'
        self.filters['cert_no'].label = 'CN #'


class CalibratedOutFilter(django_filters.FilterSet):
    class Meta:
        model = Tools_Calibrated
        fields = ['description', 'cert_no', 'workorder_no', ]

    def __init__(self, *args, **kwargs):
        super(CalibratedOutFilter, self).__init__(*args, **kwargs)

        self.filters['cert_no'].label = 'CN #'
        self.filters['workorder_no'].label = 'WorkOrder #'


class UnCalibratedOutFilter(django_filters.FilterSet):
    class Meta:
        model = Tools_UnCalibrated
        fields = ['description', 'part_number', 'workorder_no']

    def __init__(self, *args, **kwargs):
        super(UnCalibratedOutFilter, self).__init__(*args, **kwargs)
        self.filters['part_number'].label = 'Part #'
        self.filters['workorder_no'].label = 'WorkOrder #'


class UnCalibratedFilter(django_filters.FilterSet):
    class Meta:
        model = Tools_UnCalibrated
        fields = ['description', 'part_number', 'serial_number']

    def __init__(self, *args, **kwargs):
        super(UnCalibratedFilter, self).__init__(*args, **kwargs)
        self.filters['part_number'].label = 'Part #'
        self.filters['serial_number'].label = 'Serial #'


class PartsFilter(django_filters.FilterSet):
    class Meta:
        model = Parts
        fields = ['SRN', 'part_type', 'part_number', 'description', ]

        widgets = {
            'SRN': forms.TextInput(attrs={'autofocus': ''}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'part_number': forms.Select(attrs={'class': 'form-control'}),
            'part_type': forms.Select(attrs={'class': 'form-control'}),

        }

    def __init__(self, *args, **kwargs):
        super(PartsFilter, self).__init__(*args, **kwargs)

        self.filters['part_number'].label = 'Part #'
        self.filters['part_type'].label = 'Part-Type'


class QuaratineFilter(django_filters.FilterSet):
    class Meta:
        model = Parts
        fields = ['description', 'part_type', 'part_number', ]

        widgets = {

            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'part_number': forms.Select(attrs={'class': 'form-control'}),
            'part_type': forms.Select(attrs={'class': 'form-control'}),

        }

    def __init__(self, *args, **kwargs):
        super(QuaratineFilter, self).__init__(*args, **kwargs)

        self.filters['part_number'].label = 'Part #'
        self.filters['part_type'].label = 'Part-Type'


class ReservedFilter(django_filters.FilterSet):
    class Meta:
        model = Parts
        fields = ['SRN', 'description', 'part_number', 'tail_number']

    def __init__(self, *args, **kwargs):
        super(ReservedFilter, self).__init__(*args, **kwargs)
        self.filters['part_number'].label = 'Part #'
        self.filters['tail_number'].label = 'Tail #'


class OHFilter(django_filters.FilterSet):

    class Meta:
        model = OrderHistory
        fields = ['description', 'part_number', 'part_type', 'ordered_by']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'part_number': forms.TextInput(attrs={'class': 'form-control'}),
            'part_type': forms.Select(attrs={'class': 'form-control'}),
            'ordered_by': forms.Select(attrs={'class': 'form-control'}),

        }


class reOrderFilter(django_filters.FilterSet):
    class Meta:
        model = ReorderItems
        fields = ['description', 'part_number', 'part_type', ]
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'part_number': forms.TextInput(attrs={'class': 'form-control'}),
            'part_type': forms.Select(attrs={'class': 'form-control'}),

        }

    def __init__(self, *args, **kwargs):
        super(reOrderFilter, self).__init__(*args, **kwargs)

        self.filters['part_number'].label = 'Part #'
        self.filters['part_type'].label = 'Part-Type'


class WorkOrderLinkPartFilter(django_filters.FilterSet):

    class Meta:
        model = PartWorkOrders
        fields = ['part__description', 'part__part_number',
                  'jobCardNumber', ]

    def __init__(self, *args, **kwargs):
        super(WorkOrderLinkPartFilter, self).__init__(*args, **kwargs)
        self.filters['jobCardNumber'].label = 'Job-Card #'
        self.filters['part__part_number'].label = 'Part #'
        self.filters['part__description'].label = 'Description'
