from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates the default analyst user if not exists'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='analyst').exists():
            User.objects.create_superuser(
                username='analyst',
                email='analyst@breatheesg.com',
                password='analyst123'
            )
            self.stdout.write(self.style.SUCCESS('Analyst user created: analyst / analyst123'))
        else:
            # reset password to ensure it's correct
            u = User.objects.get(username='analyst')
            u.set_password('analyst123')
            u.save()
            self.stdout.write(self.style.SUCCESS('Analyst user already exists, password reset to analyst123'))
