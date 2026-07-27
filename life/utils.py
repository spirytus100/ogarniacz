import datetime
from .models import Activity

def calculate_streak():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    # 1. Pobieramy wszystkie unikalne daty z bazy i zamieniamy je na zbiór (set)
    # Używamy .distinct(), żeby nie pobierać powtarzających się dat 
    # (jeśli np. jednego dnia masz 3 wpisy o nauce)
    activity_dates = set(Activity.objects.values_list('date', flat=True).distinct())

    # Jeśli nie ma żadnych aktywności, streak wynosi 0
    if not activity_dates:
        return 0

    # 2. Sprawdzamy czy streak w ogóle "żyje"
    # Żyje tylko wtedy, gdy uczyliśmy się dzisiaj LUB wczoraj
    if today not in activity_dates and yesterday not in activity_dates:
        return 0

    # 3. Zliczamy dni wstecz
    streak = 0
    
    # Ustalamy dzień początkowy do odliczania
    current_date = today if today in activity_dates else yesterday

    # Dopóki cofając się w czasie znajdujemy datę w naszych aktywnościach,
    # zwiększamy streak i cofamy się o kolejny 1 dzień.
    while current_date in activity_dates:
        streak += 1
        current_date -= datetime.timedelta(days=1)

    return streak