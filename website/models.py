from django.db import models

# Create your models here.


class ScamReport(models.Model):
    INITIATIVE_CHOICES = [
        ('federal', 'Federal Program'),
        ('state', 'State Program'),
        ('ngo', 'NGO'),
        ('other', 'Other'),
    ]

    initiative_type = models.CharField(max_length=50, choices=INITIATIVE_CHOICES)
    whatsapp = models.BooleanField(default=False)
    facebook = models.BooleanField(default=False)
    email = models.BooleanField(default=False)
    other = models.BooleanField(default=False)
    reference = models.CharField(max_length=255, blank=True, null=True)
    screenshots = models.FileField(upload_to='scam_screenshots/', blank=True, null=True)
    description = models.TextField()
    contact = models.CharField(max_length=150, blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.initiative_type} - {self.reference or 'No Ref'}"
