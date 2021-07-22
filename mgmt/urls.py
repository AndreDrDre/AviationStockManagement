from django.urls import path
from django.contrib.auth import views as auth_views
from mgmt import views

urlpatterns = [
    path('', views.signin, name='signin'),
    path('register/', views.register, name='register'),
    path('logoutUser/', views.logoutUser, name='logoutUser'),

    path('home/', views.home, name='home'),


    path('admin/', views.adminpage, name='adminpage'),



    # General Routing

    #Store Logic -------------------------------------------------#
    path('shoppingList/', views.shoppingList, name='shoppingList'),

    path('RecieveShop/<str:pk>/', views.RecieveShop, name='RecieveShop'),
    path('IssueOutShop/<str:pk>/', views.IssueOutShop, name='IssueOutShop'),
    path('OrderShop/<str:pk>/', views.OrderShop, name='OrderShop'),

    path('editShop/<str:pk>/', views.editShop, name='editShop'),
    path('shoppingListForm/',
         views.shoppingListForm, name='shoppingListForm'),


    path('PartsHistory/', views.PartsHistory, name='PartsHistory'),
    path('store/', views.store, name='store'),
    path('inventory', views.inventory, name='inventory'),
    path('Rinventory', views.Rinventory, name='Rinventory'),
    path('Qinventory', views.Qinventory, name='Qinventory'),
    path('repair/<str:pk>/', views.repair, name='repair'),
    path('repairReturn/<str:pk>/', views.repairReturn, name='repairReturn'),

    path('edit_part/<str:pk>/', views.edit_part, name="edit_part"),

    path('recieveorder/<str:pk>/', views.recieveorder, name='recieveorder'),
    path('createneworder/<str:pk>', views.createneworder, name='createneworder'),
    path('issuePart/<str:pk>/', views.issuePart, name='issuePart'),

    path('addToInventory/<str:Type>/',
         views.addToInventory, name='addToInventory'),

    #-------------------------------------------------------------#

    #Historical Logic -------------------------------------------------#
    path('historialWO/<str:pk>/', views.historialWO, name='historialWO'),

    path('historical_inventory', views.historical_inventory,
         name='historical_inventory'),

    #-------------------------------------------------------------#



    # Order Part-----------------------------------------------#
    path('orderpart/', views.orderpart, name='orderpart'),
    path('orderhistory/', views.orderhistory, name='orderhistory'),
    path('exportorder/', views.exportorder, name='exportorder'),
    path('deletepart/<str:pk>/', views.deletepart, name='deletepart'),
    path('waybill/<str:pk>/', views.waybill, name='waybill'),
    path('pricechange/<str:pk>/', views.pricechange, name='pricechange'),
    path('exportstatus/<str:pk>/', views.exportstatus, name='exportstatus'),
    path('InterimOrder/', views.InterimOrder, name='InterimOrder'),
    path('interimtransfer/', views.interimtransfer, name='interimtransfer'),
    path('addToQuarentine', views.addToQuarentine, name='addToQuarentine'),
    path('instructions/<str:pk>/', views.instructions, name='instructions'),

    path('exportstatusdel/<str:pk>/',
         views.exportstatusdel, name='exportstatusdel'),

    path('exportXlsOrderhistory/', views.exportXlsOrderHistory,
         name='exportXlsOrderHistory'),
    #----------------------------------------------------------#





    # Work-orders and related parts-----------------------------#

    path('WorkOrderHistory/', views.WorkOrderHistory, name='WorkOrderHistory'),
    path('workorders/', views.workorders, name='workorders'),

    path('partslink/<str:pk>/<str:Type>/', views.partslink, name='partslink'),


    path('sendhometoolCali/<str:pk>/',
         views.sendhometoolCali, name='sendhometoolCali'),
    path('sendhometoolUnCali/<str:pk>/',
         views.sendhometoolUnCali, name='sendhometoolUnCali'),
    path('changeWorkOrderUnCali/<str:pk>/',
         views.changeWorkOrderUnCali, name='changeWorkOrderUnCali'),
    path('changeWorkOrderCali/<str:pk>/',
         views.changeWorkOrderCali, name='changeWorkOrderCali'),

    path('change_order_status/<str:pk>/',
         views.change_order_status, name='change_order_status'),

    path('deleteWO/<str:pk>/', views.deleteWO, name='deleteWO'),

    path('deleteWOpartlink/<str:pk>/',
         views.deleteWOpartlink, name='deleteWOpartlink'),

    path('InhouseReapirs/', views.InhouseReapirs, name='InhouseReapirs'),

    path('ShopReapirs/', views.ShopReapirs, name='ShopReapirs'),

    path('transportInfo/<str:pk>/', views.transportInfo, name='transportInfo'),






    #-----------------------------------------------------------#


    # Tools -----------------------------#
    path('tools/', views.tools, name='tools'),
    path('deleteUnCali/<str:pk>/', views.deleteUnCali, name='deleteUnCali'),
    path('deleteCali/<str:pk>/', views.deleteCali, name='deleteCali'),
    path('editCali/<str:pk>/', views.editCali, name='editCali'),
    path('editUnCali/<str:pk>/', views.editUnCali, name='editUnCali'),
    path('calicomplete/<str:pk>/', views.calicomplete, name='calicomplete'),
    path('toolinstructions//<str:pk>/',
         views.toolinstructions, name='toolinstructions'),

    path('issueworkorderCali/<str:pk>/',
         views.issueworkorderCali, name='issueworkorderCali'),

    path('issueUnCali/<str:pk>/',
         views.issueUnCali, name='issueUnCali'),

    path('change_calibration_status/<str:pk>/',
         views.change_calibration_status, name='change_calibration_status'),
    #-----------------------------------------------------------#


    #Exporting files----------------------------------------------#

    path(r'exportCali/xls/', views.exportXlsxCali, name='exportXlsxCali'),
    path(r'exportUncali/xls/', views.exportXlsxUnCali, name='exportXlsxUnCali'),
    path(r'exportXlsInventory/xls/<str:Type>/',
         views.exportXlsInventory, name='exportXlsInventory'),

    #pdf-----------------------------------------------#
    path('exportPDForder/', views.exportPDForder, name='exportPDForder'),

    path('exportPDFWorkorder/<str:pk>/',
         views.exportPDFWorkorder, name='exportPDFWorkorder'),

    #-------------------------------------------------------------#

    #Re-Order Parts-----------------------------------------------#
    path('reorderParts/', views.reorderParts, name="reorderParts"),


    path('reorder_level/<str:pk>/', views.reorder_level, name="reorder_level"),

    path('quickOrder/<str:pk>/', views.quickOrder, name="quickOrder"),

    path('pdf_report_create/<str:pk>/',
         views.pdf_report_create, name="pdf_report_create"),



    #-------------------------------------------------------------#









]
