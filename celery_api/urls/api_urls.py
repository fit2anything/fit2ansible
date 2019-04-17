from django.urls import path

from .. import api

app_name = 'celery-api'

urlpatterns = [
    path('tasks/<uuid:pk>/result/', api.TaskResultApi.as_view(), name='task-result-api'),
    path('tasks/<uuid:pk>/log/', api.TaskLogApi.as_view(), name='task-log-api'),
    # 兼容之前版本
    path('celery/task/<uuid:pk>/result/', api.IMTaskResultApi.as_view(), name='celery-task-result-api'),
    path('celery/task/<uuid:pk>/log/', api.TaskLogApi.as_view(), name='celery-task-log-api'),
]
