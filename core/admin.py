from django.contrib import admin

from .models import Parcelle, CapteurData, IrrigationDecision, Mesure

admin.site.register(Parcelle)
admin.site.register(CapteurData)
admin.site.register(IrrigationDecision)
admin.site.register(Mesure)

