# coding: utf-8

from typing import ClassVar, Dict, List, Tuple
from fastapi import File, UploadFile
from fastapi.responses import FileResponse  # noqa: F401

from openapi_server.models.cloud_configuration import CloudConfiguration
from openapi_server.models.cloud_configuration_create_request import CloudConfigurationCreateRequest
from openapi_server.models.cloud_configuration_list import CloudConfigurationList
from openapi_server.models.cloud_configuration_update_request import CloudConfigurationUpdateRequest


class BaseConfigCloudApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseConfigCloudApi.subclasses = BaseConfigCloudApi.subclasses + (cls,)
    def create_cloud_configuration(
        self,
        cloud_configuration_create_request: CloudConfigurationCreateRequest,
    ) -> CloudConfiguration:
        ...


    def delete_cloud_configuration(
        self,
        id: str,
    ) -> None:
        ...


    def get_cloud_configuration(
        self,
        id: str,
    ) -> CloudConfiguration:
        ...


    def list_cloud_configurations(
        self,
    ) -> CloudConfigurationList:
        ...


    def update_cloud_configuration(
        self,
        id: str,
        cloud_configuration_update_request: CloudConfigurationUpdateRequest,
    ) -> CloudConfiguration:
        ...
