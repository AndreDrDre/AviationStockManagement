from django.db import models
import datetime
from datetime import timedelta, datetime
from django.utils import timezone
from django.db.models import F
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
from datetime import datetime
import random
from django.contrib.auth.models import User


PARTTYPE_CHOICES = (
    ("Rotable", "Rotable"),
    ("Tires", "Tires"),
    ("AGS", "AGS"),
    ("Consumables", "Consumables"),
    ("Shelf-life", "Shelf-life"),

)
CONDITIONS = (
    ("NEW", "NEW"),
    ("OH", "OH"),
    ("AR", "AR"),
    ("SV", "SV"),
    ("REPAIRABLE", "REPAIRABLE"),
    ("DAMAGED", "DAMAGED"),
    ("INCORRECT-DOC", "INCORRECT-DOC"),
    ("WRONG-PART", "WRONG-PART"),

)
REPAIRS = (
    ("INHOUSE", "INHOUSE"),
    ("SHOP", "SHOP"),
)


class TailNumber(models.Model):

    name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        if self is not None:
            return self.name


class Employees(models.Model):

    name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        if self is not None:
            return self.name


class Profile(models.Model):
    user = models.OneToOneField(
        User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name


def calculateCheck(EAN13):
    listIntheck = []
    checkdigit = 0
    ean13Final = ""
    for char in EAN13:
        listIntheck.append(int(char))

    combination = sum(listIntheck[0::2]) + sum(listIntheck[1::2])*3
    unitdigit = str(combination)[-1]

    if int(unitdigit) == 0:
        checkdigit = 0
        ean13Final = EAN13 + str(checkdigit)
    else:
        checkdigit = 10 - int(unitdigit)
        ean13Final = EAN13 + str(checkdigit)

    return ean13Final


class WorkOrders(models.Model):
 # Add new aircraft here

    WORKORDER_CHOICES = (
        ("OPEN", "OPEN"),
        ("COMPLETED", "COMPLETED"),
    )

    tail_number = models.ForeignKey(
        TailNumber, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Tail #")
    status = models.CharField(
        max_length=20, choices=WORKORDER_CHOICES, default='OPEN')
    description = models.TextField(blank=True, null=True)
    type_airframe = models.CharField(max_length=50, blank=True, null=True)
    date_added = models.DateTimeField(auto_now=True)
    date_closed = models.DateTimeField(
        auto_now_add=False, blank=True, null=True)
    ldgs_at_open = models.IntegerField(default='0', blank=True, null=True)
    hours_at_open = models.IntegerField(default='0', blank=True, null=True)
    workorder_number = models.CharField(max_length=50, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def duration(self):
        date_open = self.date_added
        date_close = self.date_closed
        total = date_close-date_open
        return str(total.days) + " days"

    def __str__(self):
        return self.workorder_number


class Parts(models.Model):
    waybill = models.CharField(max_length=50, blank=True, null=True)
    urlWayBill = models.URLField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=50, blank=True, null=True)
    part_number = models.CharField(max_length=50, blank=True, null=True)
    serial_number = models.CharField(max_length=50, blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    jobCardNumber = models.CharField(max_length=50, blank=True, null=True)
    Historical = models.BooleanField(default='False', blank=True, null=True)
    batch_no = models.CharField(max_length=50, blank=True, null=True)
    expiry_date = models.DateTimeField(
        auto_now_add=False, blank=True, null=True)
    quantity = models.IntegerField(default='0', blank=True, null=True)
    reorder_level = models.IntegerField(default='0', blank=True, null=True)

    # For receieving partial orders pertainng to AGS, Consumables and Shelflife
    receive_quantity = models.IntegerField(default='0', blank=True, null=True)
    order_quantity = models.IntegerField(default='0', blank=True, null=True)
    issue_quantity = models.IntegerField(default='0', blank=True, null=True)

    ipc_reference = models.CharField(max_length=50, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now=True)
    date_received = models.DateTimeField(
        auto_now_add=False, blank=True, null=True)

    ticketed = models.BooleanField(default='False', blank=True, null=True)
    recieve_part = models.BooleanField(default='False')

    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    vendor = models.CharField(max_length=50, blank=True, null=True)
    purchase_order_number = models.CharField(
        max_length=50, blank=True, null=True, verbose_name='PurchaseOrder #')

    Repaired = models.BooleanField(default='False', blank=True, null=True)
    Quarentine = models.BooleanField(default='False', blank=True, null=True)
    exported = models.BooleanField(default='False', blank=True, null=True)

    bin_number = models.CharField(max_length=50, blank=True, null=True)

    cert_document = models.ImageField(upload_to="Cert-Parts",
                                      blank=True, null=True, verbose_name='Certification Document')
    SRN = models.CharField(max_length=50, blank=True, null=True)
    barcode = models.ImageField(
        upload_to="barcode-Parts", blank=True, null=True)

    inspector = models.ForeignKey(
        Employees, null=True, blank=True, related_name='inspector', on_delete=models.SET_NULL, verbose_name="Inspector:")

    ordered_by = models.ForeignKey(
        Employees, null=True, blank=True, related_name='ordered_by', on_delete=models.SET_NULL, verbose_name="Ordered by:")

    tail_number = models.ForeignKey(
        TailNumber, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Tail #")

    issued_by = models.ForeignKey(
        Employees, null=True, blank=True, related_name='issued_by', on_delete=models.SET_NULL, verbose_name="Issued by:")

    part_type = models.CharField(
        max_length=20, choices=PARTTYPE_CHOICES, default='Rotable', verbose_name="Part-Type")
    condition = models.CharField(
        max_length=20, choices=CONDITIONS, default='NEW')

    repaired_by = models.CharField(max_length=20, choices=REPAIRS, default='')

    workorders = models.ManyToManyField(
        WorkOrders, through='PartWorkOrders', related_name='parts', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.barcode == None:
            number = 0
            EAN = barcode.get_barcode_class('ean13')
            now = datetime.now()
            year = now.strftime("%Y%m%d")
            number = random.randint(1000, 9999)
            year = year+str(number)
            self.SRN = calculateCheck(year)
            ean = EAN(year, writer=ImageWriter())
            buffer = BytesIO()
            ean.write(buffer)
            self.barcode.save(self.SRN+'.png', File(buffer), save=False)
            return super().save(*args, **kwargs)
        else:
            try:
                this = Parts.objects.get(id=self.id)
                if this.cert_document != self.cert_document:
                    this.cert_document.delete(save=True)
            except:
                pass
            super(Parts, self).save(*args, **kwargs)

    def __str__(self):
        if self is not None:
            return '{} : {} : {}'.format(
                str(self.user),
                str(self.description),
                str(self.part_number))


class PartWorkOrders(models.Model):

    part = models.ForeignKey(
        Parts, null=True, on_delete=models.SET_NULL)
    workorder = models.ForeignKey(
        WorkOrders, null=True, on_delete=models.SET_NULL)
    issue_quantity = models.IntegerField(default='0', blank=True, null=True)

    price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    removed_from = models.CharField(max_length=50, blank=True, null=True)
    removed_by = models.CharField(max_length=50, blank=True, null=True)

    cert_document = models.ImageField(
        blank=True, null=True, verbose_name='Certification Document')

    jobCardNumber = models.CharField(max_length=50, blank=True, null=True)

    receivedRepair = models.BooleanField(
        default='False', blank=True, null=True)

    # issued_by = models.ForeignKey(
    #     Employees, null=True, blank=True, related_name='issued_by', on_delete=models.SET_NULL, verbose_name="Issued by:")

    issued_by = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total(self):
        price = self.price*self.issue_quantity
        return price

    def __str__(self):
        if self is not None:
            return '{} : {} : {} : {} :{} :{}: {}'.format(
                str(self.part),
                str(self.workorder),
                str(self.issue_quantity),
                str(self.price),
                str(self.jobCardNumber),
                str(self.total),
                str(self.receivedRepair))


class OrderHistory(models.Model):

    description = models.CharField(max_length=50, blank=True, null=True)
    part_number = models.CharField(max_length=50, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now=True)

    order_quantity = models.IntegerField(
        default='0', blank=True, null=True)

    ipc_reference = models.CharField(max_length=50, blank=True, null=True)
    vendor = models.CharField(max_length=50, blank=True, null=True)
    ordered_by = models.CharField(max_length=50, blank=True, null=True)
    tail_number = models.CharField(max_length=50, blank=True, null=True)
    part_type = models.CharField(
        max_length=20,
        choices=PARTTYPE_CHOICES,
        default='Rotable',
        verbose_name="Part-Type"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.description


class Tools_Calibrated(models.Model):
    description = models.CharField(max_length=50, blank=True, null=True)
    serial_number = models.CharField(max_length=50, blank=True, null=True)
    part_number = models.CharField(max_length=50, blank=True, null=True)
    recieved = models.DateTimeField(auto_now_add=False, auto_now=True)
    calibrated = models.BooleanField(default='True', blank=True, null=True)
    calibrated_date = models.DateTimeField(
        auto_now_add=False, blank=True, null=True)
    expiry_date = models.DateTimeField(
        auto_now_add=False, blank=True, null=True)
    cert_no = models.CharField(max_length=50, blank=True, null=True)

    calibration_certificate = models.ImageField(upload_to="Cert-Tools",
                                                blank=True, null=True, verbose_name='Certification Document')

    range_no = models.CharField(max_length=50, blank=True, null=True)

    issued = models.BooleanField(default='False', blank=True, null=True)
    barcode = models.ImageField(upload_to="barcode-calibrated",
                                blank=True, null=True)
    workorder_no = models.ForeignKey(
        WorkOrders, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def timecalculated(self):
        exp = self.expiry_date
        now = timezone.now()
        total = (exp-now).days

        return int(total)+1

    def save(self, *args, **kwargs):
        if self.barcode == None:
            number = 0
            EAN = barcode.get_barcode_class('ean13')
            now = datetime.now()  # current date and time
            year = now.strftime("%Y%m%d")
            number = random.randint(1000, 9999)
            year = year+str(number)

            self.cert_no = calculateCheck(year)

            ean = EAN(year, writer=ImageWriter())
            buffer = BytesIO()
            ean.write(buffer)
            self.barcode.save('barcode.png', File(buffer), save=False)
            return super().save(*args, **kwargs)
        else:
            try:
                this = Tools_Calibrated.objects.get(id=self.id)
                if this.calibration_certificate != self.calibration_certificate:
                    this.calibration_certificate.delete(save=True)
            except:
                pass  # when new photo then we do nothing, normal case
            super(Tools_Calibrated, self).save(*args, **kwargs)

    def __str__(self):
        return self.description


class Tools_UnCalibrated(models.Model):

    description = models.CharField(max_length=50, blank=True, null=True)
    serial_number = models.CharField(max_length=50, blank=True, null=True)
    part_number = models.CharField(max_length=50, blank=True, null=True)
    recieved = models.DateTimeField(auto_now_add=False, auto_now=True)
    issued = models.BooleanField(default='False', blank=True, null=True)
    # calibrated special Tool

    workorder_no = models.ForeignKey(
        WorkOrders, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.description


class ToolChecker(models.Model):
    TOOL_CHOICES = (
        (0, "Calibrated"),
        (1, "Un-Calibrated"),

    )

    tool_type = models.IntegerField(
        choices=TOOL_CHOICES,
        default=1
    )

    def __str__(self):
        return self.tool_type


class ReorderItems(models.Model):

    part_type = models.CharField(
        max_length=20,
        choices=PARTTYPE_CHOICES,
        default='Rotable',
        verbose_name="Part-Type"
    )

    description = models.CharField(max_length=50, blank=True, null=True)
    part_number = models.CharField(max_length=50, blank=True, null=True)
    ipc_reference = models.CharField(max_length=50, blank=True, null=True)

    tail_number = models.CharField(max_length=50, blank=True, null=True)

    date_ordered = models.DateTimeField(auto_now=True)
    price = models.IntegerField(blank=True, null=True)

    reorder_level = models.IntegerField(
        default='0', blank=True, null=True)
    quantity = models.IntegerField(
        default='0', blank=True, null=True)

    order_quantity = models.IntegerField(
        default='0', blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        if self is not None:
            return '{} : {} : {}'.format(
                str(self.user),
                str(self.description),
                str(self.part_number))
