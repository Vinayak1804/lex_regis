from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Clears the demo users from the database'

    def handle(self, *args, **kwargs):
        demo_users = User.objects.filter(email__endswith='.demo@lexregis.local')
        count = demo_users.count()
        demo_users.delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} demo users and their related data!'))
