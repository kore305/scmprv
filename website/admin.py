from django.contrib import admin


from .models import ScamReport

@admin.register(ScamReport)
class ScamReportAdmin(admin.ModelAdmin):
    list_display = ('initiative_type', 'reference', 'contact', 'submitted_at')
    search_fields = ('reference', 'contact')
    list_filter = ('initiative_type', 'submitted_at')