from django.core.management.base import BaseCommand
from whatsapp_verifier.models import FederalProgram
import pandas as pd
import os

class Command(BaseCommand):
    help = 'Import federal programs from Excel file'
    
    def handle(self, *args, **options):
        excel_path = 'nigeria_federal_programs_comprehensive.xlsx'
        
        try:
            df = pd.read_excel(excel_path)
            FederalProgram.objects.all().delete()
            
            for index, row in df.iterrows():
                FederalProgram.objects.create(
                    name=row['name'],
                    sector=row['sector'],
                    level=row['level'],
                    agency=row['agency'],
                    link=row['link']
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {len(df)} federal programs')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing programs: {e}')
            )