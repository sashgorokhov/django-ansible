from django.conf import settings as django_settings


DJANGO_ANSIBLE = getattr(django_settings, 'DJANGO_ANSIBLE', dict())
DJANGO_ANSIBLE.setdefault('SERVER_ADDRESS', 'http://127.0.0.1')

