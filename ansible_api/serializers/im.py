# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from .inventory import InventorySerializer
from .playbook import PlaySerializer
from .adhoc import AdHocSerializer


__all__ = ['IMPlaybookSerializer', 'IMAdHocSerializer']


class IMBaseSerializer(serializers.Serializer):
    inventory = InventorySerializer(required=False)

    project = None
    inv_serializer = None

    def check_inventory(self):
        hosts = self.initial_data.get("inventory", {}).get("hosts")
        if not hosts:
            raise serializers.ValidationError("hosts is null")

        for host in hosts:
            if not host.get('name'):
                raise serializers.ValidationError({"hosts", "name is null"})

    def is_valid(self, raise_exception=False):
        self.check_inventory()
        return super().is_valid(raise_exception=raise_exception)


class IMPlaybookSerializer(IMBaseSerializer):
    plays = PlaySerializer(many=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class IMAdHocSerializer(IMBaseSerializer):
    adhoc = AdHocSerializer(required=True)

    project = None
    inv_serializer = None

    def create(self, validated_data):
        pass

    def is_valid(self, raise_exception=False):
        adhoc_data = self.initial_data.get('adhoc')
        if not adhoc_data.get("pattern"):
            raise serializers.ValidationError("pattern is null")
        elif not adhoc_data.get("module"):
            raise serializers.ValidationError("module is null")
        return super().is_valid()

    def update(self, instance, validated_data):
        pass
