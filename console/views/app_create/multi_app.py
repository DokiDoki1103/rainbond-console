# -*- coding: utf8 -*-
import logging

from rest_framework.response import Response
from www.utils.return_message import general_message
from django.views.decorators.cache import never_cache
from console.views.base import RegionTenantHeaderView
from console.services.multi_app_service import multi_app_service

logger = logging.getLogger("default")


class MultiAppCheckView(RegionTenantHeaderView):
    @never_cache
    def get(self, request, *args, **kwargs):
        """
        multiple application check
        ---
        parameters:
            - name: check_uuid
              description: Universally Unique Identifier for asynchronous check task
              required: true
              type: string
              paramType: query
        """
        check_uuid = request.GET.get("check_uuid", None)
        if not check_uuid:
            return Response(general_message(400, "params error", "the field 'check_uuid' is required"), status=400)

        code, msg, msg_show, services = multi_app_service.list_services(self.response_region, self.tenant, check_uuid)
        if code != 200:
            result = general_message(code, msg, msg_show)
        else:
            result = general_message(
                code, "successfully entered the multi-service creation process", "成功进入多组件创建流程", list=services)
        return Response(data=result, status=200)


class MultiAppCreateView(RegionTenantHeaderView):
    @never_cache
    def post(self, request, *args, **kwargs):
        """
        multiple-service application creation
        ---
        parameters:
            - name: service_alias
              description: service alias
              required: true
              type: string
              paramType: form
        parameters:
            - name: group_id
              description: Universally Unique Identifier for group
              required: true
              type: string
              paramType: form

        """
        service_alias = kwargs.get("serviceAlias", None)
        resp = validate_request(service_alias, "serviceAlias")
        if resp:
            return resp
        service_infos = request.data.get("service_infos", None)
        resp = validate_request(service_infos, "service_infos")
        if resp:
            return resp

        code, msg, msg_show, group_id = multi_app_service.create_services(
            region_name=self.response_region,
            tenant=self.tenant,
            user=self.user,
            service_alias=service_alias,
            service_infos=service_infos)

        result = general_message(code, msg, msg_show, bean=group_id)

        return Response(result, status=result["code"])


def validate_request(item, name):
    if not item:
        return Response(general_message(400, "params error", "the field '" + name + "' is required"), status=400)
    return None
