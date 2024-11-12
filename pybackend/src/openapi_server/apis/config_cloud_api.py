# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.config_cloud_api_base import BaseConfigCloudApi
import openapi_server.impl

from fastapi.responses import FileResponse
from fastapi import File, UploadFile
from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from openapi_server.models.cloud_configuration import CloudConfiguration
from openapi_server.models.cloud_configuration_create_request import CloudConfigurationCreateRequest
from openapi_server.models.cloud_configuration_list import CloudConfigurationList
from openapi_server.models.cloud_configuration_update_request import CloudConfigurationUpdateRequest


router = APIRouter(prefix="/api/v1")

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/configurations/cloud",
    responses={
        200: {"model": CloudConfiguration, "description": "Cloud configuration"},
    },
    tags=["config_cloud"],
    summary="Create a cloud configuration",
    response_model_by_alias=True,
)
def create_cloud_configuration(
    cloud_configuration_create_request: CloudConfigurationCreateRequest = Body(None, description=""),
) -> CloudConfiguration:
    if not BaseConfigCloudApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return BaseConfigCloudApi.subclasses[0]().create_cloud_configuration(cloud_configuration_create_request)


@router.delete(
    "/configurations/cloud/{id}",
    responses={
        200: {"description": "Cloud configuration deleted"},
    },
    tags=["config_cloud"],
    summary="Delete a cloud configuration",
    response_model_by_alias=True,
)
def delete_cloud_configuration(
    id: str = Path(..., description=""),
) -> None:
    if not BaseConfigCloudApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return BaseConfigCloudApi.subclasses[0]().delete_cloud_configuration(id)


@router.get(
    "/configurations/cloud/{id}",
    responses={
        200: {"model": CloudConfiguration, "description": "Cloud configuration"},
    },
    tags=["config_cloud"],
    summary="Get a cloud configuration",
    response_model_by_alias=True,
)
def get_cloud_configuration(
    id: str = Path(..., description=""),
) -> CloudConfiguration:
    if not BaseConfigCloudApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return BaseConfigCloudApi.subclasses[0]().get_cloud_configuration(id)


@router.get(
    "/configurations/cloud",
    responses={
        200: {"model": CloudConfigurationList, "description": "List of clouds"},
    },
    tags=["config_cloud"],
    summary="List cloud configurations",
    response_model_by_alias=True,
)
def list_cloud_configurations(
) -> CloudConfigurationList:
    if not BaseConfigCloudApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return BaseConfigCloudApi.subclasses[0]().list_cloud_configurations()


@router.put(
    "/configurations/cloud/{id}",
    responses={
        200: {"model": CloudConfiguration, "description": "Cloud configuration"},
    },
    tags=["config_cloud"],
    summary="Update a cloud configuration",
    response_model_by_alias=True,
)
def update_cloud_configuration(
    id: str = Path(..., description=""),
    cloud_configuration_update_request: CloudConfigurationUpdateRequest = Body(None, description=""),
) -> CloudConfiguration:
    if not BaseConfigCloudApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return BaseConfigCloudApi.subclasses[0]().update_cloud_configuration(id, cloud_configuration_update_request)
