from rest_framework import serializers
from django.shortcuts import reverse

from ansible_api.serializers import HostSerializer, GroupSerializer, ProjectSerializer
from .models import Cluster, Node, Role, DeployExecution, Offline


# 离线包序列化类
class OfflineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offline
        fields = [
            'name', 'path', 'remark', 'is_active', 'content_yml'
        ]


class ClusterSerializer(ProjectSerializer):
    # offline = OfflineSerializer(many=False)
    create_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Cluster
        fields = ['id', 'name', 'offline_name', 'status', 'create_time','offline']
        read_only_fields = ['id']


#节点序列化器
class NodeSerializer(serializers.ModelSerializer):
    #设置只写字段，返回数据的时候不显示
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Node
        fields = ['name','ip', 'roles', 'status', 'comment','username','password']


# class NodeSerializer(HostSerializer):
#     roles = serializers.SlugRelatedField(
#         many=True, read_only=False, queryset=Role.objects.all(),
#         slug_field='name', required=False,
#     )
#
#     class Meta:
#         model = Node
#         extra_kwargs = HostSerializer.Meta.extra_kwargs
#         read_only_fields = list(filter(lambda x: x not in ('groups',), HostSerializer.Meta.read_only_fields))
#         fields = list(filter(lambda x: x not in ('groups',), HostSerializer.Meta.fields))
#
#     def get_field_names(self, declared_fields, info):
#         names = super().get_field_names(declared_fields, info)
#         names.append('roles')
#         return names
#
#     def create(self, validated_data):
#         validated_data['groups'] = validated_data.pop('roles', [])
#         return super().create(validated_data)


class RoleSerializer(GroupSerializer):
    nodes = serializers.SlugRelatedField(
        many=True, read_only=False, queryset=Node.objects.all(),
        slug_field='name', required=False
    )

    class Meta:
        model = Role
        fields = ["id", "name", "nodes", "children", "vars", "comment"]
        read_only_fields = ["id", "children", "vars"]



class DeployReadExecutionSerializer(serializers.ModelSerializer):
    result_summary = serializers.JSONField(read_only=True)
    log_url = serializers.SerializerMethodField()
    log_ws_url = serializers.SerializerMethodField()

    class Meta:
        model = DeployExecution
        fields = [
            'id', 'state', 'num', 'result_summary', 'result_raw',
            'date_created', 'date_start', 'date_end',
        ]
        read_only_fields = [
            'id', 'state', 'num', 'result_summary', 'result_raw',
            'date_created', 'date_start', 'date_end'
        ]

    @staticmethod
    def get_log_url(obj):
        return reverse('celery-api:task-log-api', kwargs={'pk': obj.id})

    @staticmethod
    def get_log_ws_url(obj):
        return '/ws/tasks/{}/log/'.format(obj.id)
