from rest_framework import viewsets

from .models import Cluster, Node, Role, DeployExecution, Offline
from .serializers import (
    ClusterSerializer, NodeSerializer, RoleSerializer,
    DeployReadExecutionSerializer, OfflineSerializer
)
from .mixin import ClusterResourceAPIMixin
from .tasks import start_deploy_execution

import os
# 导入离线包路径
from fit2ansible.settings import OFFLINES_DIR


# 集群视图
class ClusterViewSet(viewsets.ModelViewSet):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer
    lookup_field = 'name'
    lookup_url_kwarg = 'name'


class NodeViewSet(ClusterResourceAPIMixin, viewsets.ModelViewSet):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer


class RoleViewSet(ClusterResourceAPIMixin, viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class DeployExecutionViewSet(ClusterResourceAPIMixin, viewsets.ModelViewSet):
    queryset = DeployExecution.objects.all()
    serializer_class = DeployReadExecutionSerializer
    read_serializer_class = DeployReadExecutionSerializer

    http_method_names = ['post', 'get', 'head', 'options']

    def perform_create(self, serializer):
        instance = serializer.save()
        start_deploy_execution.apply_async(
            args=(instance.id,), task_id=str(instance.id)
        )
        return instance


# 离线包视图
class OfflineViewSet(viewsets.ModelViewSet):
    queryset = Offline.objects.all()
    serializer_class = OfflineSerializer
    http_method_names = ['get', 'head', 'options']
    lookup_field = 'name'

    def get_queryset(self):
        all_offline_dir = os.listdir(OFFLINES_DIR)

        if all_offline_dir:
            for offline_dir in all_offline_dir:
                # 获取文件夹里的内容，并读取
                if not self.queryset.filter(name=offline_dir):
                    # 读取文件内容并保存
                    all_offline_file = os.listdir(os.path.join(OFFLINES_DIR, offline_dir))
                    for offline_file in all_offline_file:
                        # 构造文件绝对路径
                        abs_file = OFFLINES_DIR + '/' + offline_dir + '/' + offline_file
                        abs_file_dir = OFFLINES_DIR + '/' + offline_dir
                        # 打开文件，读取文件内容
                        with open(abs_file, 'r') as f:
                            if abs_file.endswith('.yml'):
                                file_content = f.read()
                                # 创建保存数据
                                Offline.objects.create(name=offline_dir,
                                                       path=abs_file_dir,
                                                       remark=offline_dir,
                                                       content_yml=file_content
                                                       )

        return super().get_queryset()
