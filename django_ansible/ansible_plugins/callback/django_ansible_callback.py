from __future__ import absolute_import

from ansible.plugins.callback.json import CallbackModule as JsonCallback
import requests
import os
from contextlib import contextmanager


@contextmanager
def handle_error(callback, message):
    try:
        yield
    except Exception as e:
        print(e)


class CallbackModule(JsonCallback):
    CALLBACK_NAME = 'django_ansible_callback'

    def __init__(self, *args, **kwargs):
        import json
        super(CallbackModule, self).__init__(*args, **kwargs)
        self.urls = os.environ.get('DJANGO_ANSIBLE_URLS')
        self.urls = json.loads(self.urls)
        self.metadata = os.environ.get('DJANGO_ANSIBLE_CALLBACK_METADATA', '{}')
        self.metadata = json.loads(self.metadata)

    def create_play(self, play):
        """
        :param ansible.playbook.play.Play play:
        """
        url = self.urls['create_play']
        response = requests.post(url, json={
            'id': str(play._uuid),
            'name': play.get_name(),
            'metadata': self.metadata
        }, timeout=10)
        response.raise_for_status()

    def update_play(self, play_id, stats):
        url = self.urls['update_play']
        response = requests.post(url, json={
            'id': str(play_id),
            'stats': stats
        }, timeout=10)
        response.raise_for_status()

    def create_task(self, play_id, task):
        """
        :param ansible.playbook.task.Task task:
        """
        url = self.urls['create_task']
        response = requests.post(url, json={
            'id': str(task._uuid),
            'play': str(play_id),
            'name': task.get_name(),
            'type': 'In progress'
        }, timeout=10)
        response.raise_for_status()

    def update_task(self, task_id, result):
        """
        :param ansible.executor.task_result.TaskResult result:
        """
        url = self.urls['update_task']
        task_type = 'Ok'
        if result.is_failed():
            task_type = 'Failed'
        elif result.is_skipped():
            task_type = 'Skipped'
        elif result.is_unreachable():
            task_type = 'Unreachable'
        response = requests.post(url, json={
            'id': str(task_id),
            'result': result._result,
            'type': task_type
        }, timeout=10)
        response.raise_for_status()

    def v2_playbook_on_play_start(self, play):
        """
        :param ansible.playbook.play.Play play:
        """
        super(CallbackModule, self).v2_playbook_on_play_start(play=play)
        self.create_play(play)

    def v2_playbook_on_task_start(self, task, is_conditional):
        """
        :param ansible.playbook.task.Task task:
        """
        super(CallbackModule, self).v2_playbook_on_task_start(task, is_conditional)
        self.create_task(self.results[-1]['play']['id'], task)

    def v2_runner_on_ok(self, result, **kwargs):
        """
        :param ansible.executor.task_result.TaskResult result:
        """
        super(CallbackModule, self).v2_runner_on_ok(result, **kwargs)
        self.update_task(self.results[-1]['tasks'][-1]['task']['id'], result)

    def v2_playbook_on_stats(self, stats):
        super(CallbackModule, self).v2_playbook_on_stats(stats)
        hosts = sorted(stats.processed.keys())
        summary = {}
        for h in hosts:
            s = stats.summarize(h)
            summary[h] = s
        self.update_play(self.results[-1]['play']['id'], summary)

    v2_runner_on_failed = v2_runner_on_ok
    v2_runner_on_unreachable = v2_runner_on_ok
    v2_runner_on_skipped = v2_runner_on_ok
