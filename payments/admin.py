from django.contrib import admin

from .models import Payment, PayoutRequest, Refund

admin.site.register(Payment)
admin.site.register(Refund)
admin.site.register(PayoutRequest)

# Register your models here.
