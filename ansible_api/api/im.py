# -*- coding: utf-8 -*-
#

"""
Immediately run adhoc and playbook
"""

import tempfile
from rest_framework import permissions, generics
from rest_framework.response import Response
import logging

from ..models import Play
from ..serializers import IMPlaybookSerializer, IMAdHocSerializer
from ..tasks import run_im_adhoc, run_im_playbook

__all__ = ['IMPlaybookApi', 'IMAdHocApi']


class IMPlaybookApi(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = IMPlaybookSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            plays_data = serializer.validated_data['plays']
            inventory_data = serializer.validated_data.get('inventory')
            plays = [Play(**p) for p in plays_data]
            plays_yaml = Play.get_plays_data(plays, fmt='yaml')
            f = tempfile.NamedTemporaryFile(mode='wt', delete=False, suffix='.yml')
            f.write(plays_yaml)
            logging.debug("Playbook path: {}".format(f.name))
            f.close()
            task = run_im_playbook.delay(f.name, inventory_data)
            return Response({'task': task.id})
        else:
            return Response({"error": serializer.errors})


class IMAdHocApi(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = IMAdHocSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        adhoc = serializer.get("adhoc")
        inventory = serializer.get("inventory")
        kwargs = {}
        timeout = self.request.query_params.get('timeout')
        if timeout:
            kwargs["soft_timeout"] = timeout
        if serializer.is_valid():
            task = run_im_adhoc.apply_async(
                args=(adhoc, inventory), **kwargs
            )
            return Response({'task': task.id})
        else:
            return Response({"error": serializer.errors})
