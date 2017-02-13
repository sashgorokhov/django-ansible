from django.conf.urls import url
from django_ansible import views

urlpatterns = [
    url(r"^play/create$", views.create_play, name='django-ansible-create-play'),
    url(r"^play/update$", views.update_play, name='django-ansible-update-play'),
    url(r"^task/create$", views.create_task, name='django-ansible-create-task'),
    url(r"^task/update$", views.update_task, name='django-ansible-update-task'),
]