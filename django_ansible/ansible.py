import json
import logging
import os
import tempfile
from contextlib import contextmanager

import yaml

from django_ansible import shell, models, utils


logger = logging.getLogger(__name__)


def ansible(host_pattern, module_name, module_args, **kwargs):
    raise NotImplementedError()


def ansible_playbook(playbook, options=None, env=None, ansible_playbook_executable='ansible-playbook', **kwargs):
    if not os.path.abspath(playbook):
        playbook = os.path.abspath(playbook)

    options = options or dict()
    if '-i' in options:
        if isinstance(options['-i'], (list, tuple)):
            options['-i'] = ','.join(options)
        if not options['-i'].endswith(','):
            options['-i'] += ','

    args = list()
    for key, value in options:
        if value is None:
            args.append(key)
        else:
            args.append(key)
            args.append(str(value))

    args.append(playbook)

    return shell.run(executable=ansible_playbook_executable, args=args, env=env, **kwargs)


def ansible_playbook_callback(playbook, metadata, options=None, env=None, **kwargs):
    env = env or dict()

    encode_json = lambda d: json.dumps(d).replace('"', '\\"')

    env.setdefault('ANSIBLE_CALLBACK_PLUGINS', os.path.join(os.path.dirname(__file__), 'ansible_plugins', 'callback'))
    env.setdefault('ANSIBLE_CALLBACK_WHITELIST', 'django_ansible_callback')
    env.setdefault('ANSIBLE_STDOUT_CALLBACK', 'django_ansible_callback')
    env.setdefault('DJANGO_ANSIBLE_CALLBACK_URLS', '"%s"' % encode_json(utils.get_callback_urls()))
    env.setdefault('DJANGO_ANSIBLE_CALLBACK_METADATA', '"%s"' % encode_json(metadata))

    return ansible_playbook(playbook, options=options, environ=env, **kwargs)


@contextmanager
def generate_playbook(template, cleanup=True):
    """
    Write `template` to temporary file and return its name.
    Delete file on context manager exit if cleanup=True.

    :param dict|list|str template: if str, just write to file, else dump as yaml and write to file
    """
    _, filename = tempfile.mkstemp('.yaml', text=True)
    with open(filename, 'w') as f:
        if isinstance(template, str):
            f.write(template)
        else:
            f.write(yaml.dump(template, default_flow_style=False, indent=4))

    try:
        yield filename
    finally:
        if cleanup:
            os.remove(filename)


def simple_playbook_executor(playbook, metadata, options=None, env=None, **kwargs):
    """
    :rtype: django_ansible.models.AnsiblePlay
    """
    with generate_playbook(playbook) as playbook_filename:
        completed_process = ansible_playbook_callback(
            playbook=playbook_filename, metadata=metadata, options=options, env=env, **kwargs)
    return models.AnsiblePlay.objects.filter(metadata=metadata).last()