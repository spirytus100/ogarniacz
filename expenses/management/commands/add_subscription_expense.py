from django.core.management.base import BaseCommand
from django.conf import settings
from expenses import models


class Command(BaseCommand):
    help = 'Dodaje subskrypcję jako wydatek do bazy danych'

    def handle(self, *args, **options):
        subscriptions = models.Subscription.objects.all()
        for subscription in subscriptions:
            expense = models.Expense(
                expense_date=models.datetime.date.today(),
                item=subscription.name,
                category_id=subscription.category_id,
                price=subscription.price,
                quantity=1,
                company=subscription.company
            )
            expense.save()

            budget, created = models.Budget.objects.get_or_create(category_id=subscription.category_id)
            budget.actual_cost += subscription.price
            budget.save()

            self.stdout.write(self.style.SUCCESS(f'Subskrypcja "{subscription.name}" została dodana jako wydatek.'))