from django.core.management.base import BaseCommand
import random
import os
from django.conf import settings
from constance import config 


class Command(BaseCommand):
    help = 'Pobiera losowe słowo ze słownika i robi coś z nim'

    def handle(self, *args, **options):
        path = os.path.join(settings.BASE_DIR, 'data', 'ozhegov.txt')
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                word_line = random.choice(lines).strip()
                index = word_line.find('|')
                word = word_line[:index].strip()
                description = word_line[index + 1:].lstrip("|").rstrip("|").capitalize()


                config.CURRENT_DAILY_WORD = word
                config.CURRENT_DAILY_WORD_DESCRIPTION = description  # Zastąp realnym opisem
            
            
            self.stdout.write(self.style.SUCCESS(f'Wylosowano słowo: {word}'))
        except Exception as e:
            self.stderr.write(f"Błąd: {e}")