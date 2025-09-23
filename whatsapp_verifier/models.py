from django.db import models
from model_utils.models import TimeStampedModel

# Create your models here.



class FederalProgram(TimeStampedModel):
    name = models.CharField(max_length=255)
    sector = models.CharField(max_length=255)
    level = models.CharField(max_length=100)
    agency = models.CharField(max_length=255)
    link = models.URLField()
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Federal Program"
        verbose_name_plural = "Federal Programs"
        
    def __str__(self):
        return self.name

class WhatsAppSession(TimeStampedModel):
    phone_number = models.CharField(max_length=20, unique=True)
    current_step = models.CharField(max_length=50, default='main_menu')
    language = models.CharField(max_length=10, default='en')
    temp_data = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.phone_number} - {self.current_step}"