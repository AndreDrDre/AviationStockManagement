from django.contrib import admin
from .models import *
from .forms import *
from django.contrib import admin


# Register your models here.


admin.site.register(Tools_Calibrated)
admin.site.register(Tools_UnCalibrated)
admin.site.register(ToolChecker)
admin.site.register(Profile)


class PartWorkOrdersAdmin(admin.ModelAdmin):
    list_display = ('part', 'workorder',
                    'issue_quantity', 'price', 'removed_from', 'removed_by', 'issued_by', 'jobCardNumber')

    # list_display_links = ('part')
    list_filter = ('workorder',)
    # list_editable = ('is_published',)
    # search_fields = ('workorder')

    list_per_page = 25


class EmployeesAdmin(admin.ModelAdmin):
    list_display = ('name', 'user',
                    )

    # list_display_links = ('part')
    list_filter = ('user',)
    # list_editable = ('is_published',)
    # search_fields = ('workorder')

    list_per_page = 25


class PartsAdmin(admin.ModelAdmin):
    list_display = ('description', 'part_number', 'quantity', 'user',
                    )

    list_filter = ('user',)

    list_per_page = 25


class WorkOrdersAdmin(admin.ModelAdmin):
    list_display = ('workorder_number', 'tail_number', 'type_airframe', 'status', 'user',
                    )

    list_filter = ('user', 'status',)

    list_per_page = 25


class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ('description', 'part_number', 'order_quantity', 'user',
                    )

    list_filter = ('user',)

    list_per_page = 25


class TailNumberAdmin(admin.ModelAdmin):
    list_display = ('name', 'type_airframe', 'serialno',
                    )

    list_filter = ('name',)

    list_per_page = 25


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('description', 'quantity',  'user'
                    )

    list_filter = ('user',)

    list_per_page = 25


class ReorderItemsAdmin(admin.ModelAdmin):
    list_display = ('description', 'part_number', 'quantity', 'reorder_level', 'user'
                    )

    list_filter = ('user',)

    list_per_page = 25


admin.site.register(ReorderItems, ReorderItemsAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(Employees, EmployeesAdmin)
admin.site.register(PartWorkOrders, PartWorkOrdersAdmin)
admin.site.register(Parts, PartsAdmin)
admin.site.register(WorkOrders, WorkOrdersAdmin)
admin.site.register(OrderHistory, OrderHistoryAdmin)
admin.site.register(TailNumber, TailNumberAdmin)
