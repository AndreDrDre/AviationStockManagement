from django.contrib import admin


from .models import *
from .forms import *
from django.contrib import admin


# Register your models here.
admin.site.register(Parts)
admin.site.register(WorkOrders)

admin.site.register(Tools_Calibrated)
admin.site.register(Tools_UnCalibrated)
admin.site.register(ToolChecker)


admin.site.register(OrderHistory)
admin.site.register(Profile)
admin.site.register(ReorderItems)

admin.site.register(Employees)
admin.site.register(TailNumber)


class PartWorkOrdersAdmin(admin.ModelAdmin):
    list_display = ('part', 'workorder',
                    'issue_quantity', 'price', 'removed_from', 'removed_by', 'issued_by', 'jobCardNumber')

    # list_display_links = ('part')
    list_filter = ('workorder',)
    # list_editable = ('is_published',)
    # search_fields = ('workorder')

    list_per_page = 25


admin.site.register(PartWorkOrders, PartWorkOrdersAdmin)
