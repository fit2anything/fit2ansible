from rest_framework import serializers
from django.shortcuts import reverse

from ansible_api.serializers import HostSerializer, GroupSerializer, ProjectSerializer
from .models import Cluster, Node, Role, DeployExecution, Package


__all__ = [
    'PackageSerializer', 'ClusterSerializer', 'NodeSerializer',
    'RoleSerializer', 'DeployReadExecutionSerializer',
]


class PackageSerializer(serializers.ModelSerializer):
    meta = serializers.JSONField()

    class Meta:
        model = Package
        read_only_fields = ['id', 'name', 'meta', 'date_created']
        fields = ['id', 'name', 'meta', 'date_created']


class ClusterSerializer(ProjectSerializer):
    package = serializers.SlugRelatedField(
        queryset=Package.objects.all(),
        slug_field='name', required=False
    )

    class Meta:
        model = Cluster
        fields = ['id', 'name', 'package', 'template', 'comment', 'date_created']
        read_only_fields = ['id', 'date_created']


class NodeSerializer(HostSerializer):
    roles = serializers.SlugRelatedField(
        many=True, queryset=Role.objects.all(),
        slug_field='name', required=False
    )
    meta = serializers.JSONField()

    def get_field_names(self, declared_fields, info):
        names = super().get_field_names(declared_fields, info)
        names.append('roles')
        return names

    def save(self, **kwargs):
        self.validated_data['groups'] = self.validated_data.pop('roles', [])
        return super().save(**kwargs)

    class Meta:
        model = Node
        extra_kwargs = HostSerializer.Meta.extra_kwargs
        fields = [
            'id', 'name', 'ip', 'username', 'password', 'vars', 'comment',
            'roles'
        ]
        read_only_fields = ['id']


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
    meta = serializers.JSONField()

    class Meta:
        model = Role
        fields = ['id', 'name', 'nodes', 'children', 'vars', 'meta', 'comment']
        read_only_fields = ['id']


class DeployReadExecutionSerializer(serializers.ModelSerializer):
    result_summary = serializers.JSONField(read_only=True)
    log_url = serializers.SerializerMethodField()
    log_ws_url = serializers.SerializerMethodField()

    class Meta:
        model = DeployExecution
        fields = '__all__'
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
