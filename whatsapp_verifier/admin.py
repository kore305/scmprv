
from django.contrib import admin
from .models import FederalProgram, WhatsAppSession

# Register your models here.


@admin.register(FederalProgram)
class FederalProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'sector', 'agency', 'level')
    search_fields = ('name', 'sector', 'agency')
    list_filter = ('sector', 'level')

@admin.register(WhatsAppSession)
class WhatsAppSessionAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'current_step', 'language', 'created')
    readonly_fields = ('created', 'modified')