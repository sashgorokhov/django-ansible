import json

from django.http import response
from django.shortcuts import get_object_or_404

from django_ansible import models, signals

# TODO: Add some security


def create_play(request):
    if request.method != 'POST':
        return response.HttpResponseNotAllowed(['POST'])
    if 'id' not in request.POST or 'name' not in request.POST or 'metadata' not in request.POST:
        return response.HttpResponseBadRequest('Parameters missing')

    request.POST['metadata'] = json.loads(request.POST['metadata'])

    ansible_play = models.AnsiblePlay.objects.create(**request.POST)
    signals.play_started.send_robust(None, play=ansible_play)
    return response.HttpResponse(ansible_play.pk)


def update_play(request):
    if request.method != 'POST':
        return response.HttpResponseNotAllowed(['POST'])
    if 'id' not in request.POST or 'stats' not in request.POST:
        return response.HttpResponseBadRequest('Parameters missing')

    ansible_play = get_object_or_404(models.AnsiblePlay, pk=request.POST['id'])
    ansible_play.stats = json.loads(request.POST['stats'])
    ansible_play.save()
    signals.play_finished.send_robust(None, play=ansible_play)
    return response.HttpResponse(ansible_play.pk)


def create_task(request):
    if request.method != 'POST':
        return response.HttpResponseNotAllowed(['POST'])
    if 'id' not in request.POST or 'play' not in request.POST or 'name' not in request.POST or 'type' not in request.POST:
        return response.HttpResponseBadRequest('Parameters missing')

    request.POST['play'] = get_object_or_404(models.AnsiblePlay, pk=request.POST['play'])

    task = models.AnsibleTask.objects.create(**request.POST)
    signals.task_started.send_robust(None, task=task)
    return response.HttpResponse(task.pk)


def update_task(request):
    if request.method != 'POST':
        return response.HttpResponseNotAllowed(['POST'])
    if 'id' not in request.POST or 'result' not in request.POST or 'type' not in request.POST:
        return response.HttpResponseBadRequest('Parameters missing')

    request.POST['result'] = json.loads(request.POST['result'])

    task = get_object_or_404(models.AnsibleTask, pk=request.POST['id'])
    task.result = request.POST['result']
    task.type = request.POST['type']
    task.save()
    signals.task_finished.send_robust(None, task=task)
    return response.HttpResponse(task.pk)