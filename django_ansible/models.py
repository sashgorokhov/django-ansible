from django.contrib.postgres.fields import JSONField
from django.db import models


class AnsiblePlay(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    stats = JSONField(null=True, blank=True)
    metadata = JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)
        get_latest_by = 'created_at'

    @property
    def finished(self):
        return self.stats is not None

    def __str__(self):
        return self.name


class AnsibleTask(models.Model):
    class TYPES:
        FAILED = 'Failed'
        OK = 'Ok'
        SKIPPED = 'Skipped'
        UNREACHABLE = 'Unreachable'
        IN_PROGRESS = 'In progress'

        ALL = [FAILED, OK, SKIPPED, UNREACHABLE, IN_PROGRESS]
        CHOICES = [(i, i) for i in ALL]

    id = models.UUIDField(primary_key=True, editable=False)
    play = models.ForeignKey(AnsiblePlay, related_name='tasks')
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=TYPES.CHOICES)

    result = JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)
        get_latest_by = 'created_at'

    def __str__(self):
        return self.play.name + ' - ' + self.name