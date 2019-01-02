from django.db.models import Q
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
        fields = ['id', 'name', 'offline_name', 'status', 'create_time', 'offline']
        read_only_fields = ['id']


#节点序列化器
class NodeSerializer(HostSerializer):
    roles = serializers.SlugRelatedField(many=True, queryset=Role.objects.all(),
                                         slug_field='name', required=False
                                         )

    def get_field_names(self, declared_fields, info):
        names = super().get_field_names(declared_fields, info)
        names.append('roles')
        return names

    def update(self, instance, validated_data):
        instance.groups.add(*(validated_data['roles']))
        node_group_list = []
        #根据机器所属角色给机器打标签
        for item in validated_data['roles']:
            if item.name == 'master':
                node_group_list.append('node-config-master-infra')
                instance.vars = {"openshift_node_group_name": node_group_list}
            if item.name == 'node':
                node_group_list.append('node-config-compute')
                instance.vars = {"openshift_node_group_name": node_group_list}
        instance.save()
        return instance

    def create(self, validated_data):
        validated_data['groups'] = validated_data.pop('roles', [])
        return super().create(validated_data)

    class Meta:
        model = Node
        # 过滤fields里只写数据
        extra_kwargs = HostSerializer.Meta.extra_kwargs
        # 过滤fields里只读数据
        read_only_fields = ['status']
        # 前端能展示的数据
        fields = ['id', 'name', 'ip', 'status', 'comment', 'username', 'password', 'vars']


# class NodeSerializer(HostSerializer):
#     roles = serializers.SlugRelatedField(
#         many=True, queryset=Role.objects.all(),
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
#
#     def create(self, validated_data):
#         validated_data['groups'] = validated_data.pop('roles', [])
#         return super().create(validated_data)


class RoleSerializer(GroupSerializer):
    nodes = serializers.SlugRelatedField(
        many=True,  queryset=Node.objects.all(),
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
