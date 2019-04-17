# -*- coding: utf-8 -*-
#

from rest_framework import generics
from celery.result import AsyncResult

from common.api import LogTailApi
from .serializers import TaskResultSerializer
from .utils import get_celery_task_log_path, format_task_result


__all__ = ['TaskResultApi', 'TaskLogApi', 'IMTaskResultApi']


class TaskResultApi(generics.RetrieveAPIView):
    serializer_class = TaskResultSerializer

    def get_object(self):
        task_id = self.kwargs.get('pk')
        task = AsyncResult(str(task_id))
        if not task:
            task = {'result': '', 'state': 'Pending'}
        return task


class IMTaskResultApi(generics.RetrieveAPIView):
    serializer_class = TaskResultSerializer

    def get_object(self):
        task_id = self.kwargs.get('pk')
        task = AsyncResult(str(task_id))
        if not task:
            task = {'result': '', 'state': 'Pending'}
        else:
            task = {
                'state': task.state,
                'result': format_task_result(task.result),
                'id': task.id
            }
        return task


class TaskLogApi(LogTailApi):
    task = None
    task_id = ''
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        self.task_id = str(kwargs.get('pk'))
        self.task = AsyncResult(self.task_id)
        return super().get(request, *args, **kwargs)

    def get_log_path(self):
        return get_celery_task_log_path(self.task_id)

    def is_end(self):
        return self.task.ready()
