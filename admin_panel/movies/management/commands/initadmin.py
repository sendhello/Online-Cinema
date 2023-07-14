from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


User = get_user_model()


class Command(BaseCommand):
    """Create superuser."""

    def handle(self, *args, **options):
        if User.objects.count() == 0 and settings.CREATE_SUPERUSER:
            username = 'admin'
            password = 'admin'
            print('Creating account for %s' % (username,))
            admin = User.objects.create_superuser(
                email='example@email.com', username=username, password=password
            )
            admin.is_active = True
            admin.is_admin = True
            admin.save()
        else:
            print('Admin accounts can only be initialized if no Accounts exist')
