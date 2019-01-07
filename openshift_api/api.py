from rest_framework import viewsets

from . import serializers
from .models import Cluster, Node, Role, DeployExecution, Package
from .mixin import ClusterResourceAPIMixin
from .tasks import start_deploy_execution


# 集群视图
class ClusterViewSet(viewsets.ModelViewSet):
    queryset = Cluster.objects.all()
    serializer_class = serializers.ClusterSerializer
    lookup_field = 'name'
    lookup_url_kwarg = 'name'


# 节点视图
class NodeViewSet(ClusterResourceAPIMixin, viewsets.ModelViewSet):
    queryset = Node.objects.all()
    serializer_class = serializers.NodeSerializer
    lookup_field = 'name'
    lookup_url_kwarg = 'name'


class RoleViewSet(ClusterResourceAPIMixin, viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = serializers.RoleSerializer


class DeployExecutionViewSet(ClusterResourceAPIMixin, viewsets.ModelViewSet):
    queryset = DeployExecution.objects.all()
    serializer_class = serializers.DeployExecutionSerializer
    read_serializer_class = serializers.DeployExecutionSerializer

    http_method_names = ['post', 'get', 'head', 'options']

    def perform_create(self, serializer):
        instance = serializer.save()
        start_deploy_execution.apply_async(
            args=(instance.id,), task_id=str(instance.id)
        )
        return instance


class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = serializers.PackageSerializer
    http_method_names = ['get', 'head', 'options']
    lookup_field = 'name'
    lookup_url_kwarg = 'name'

    def get_queryset(self):
        Package.lookup()
        return super().get_queryset()
