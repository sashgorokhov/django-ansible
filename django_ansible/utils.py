from urllib.parse import urljoin

from django_ansible import settings
from django.urls import reverse


def get_callback_urls():
    mkurl = lambda url: urljoin(settings.DJANGO_ANSIBLE['SERVER_ADDRESS'], url)
    return {
        'create_play': mkurl(reverse('django-ansible-create-play')),
        'update_play': mkurl(reverse('django-ansible-update-play')),
        'create_task': mkurl(reverse('django-ansible-create-task')),
        'update_task': mkurl(reverse('django-ansible-update-task')),
    }