# ##############################################################################
#  CLOUDERA APPLIED MACHINE LEARNING PROTOTYPE (AMP)
#  (C) Cloudera, Inc. 2024
#  All rights reserved.
#
#  Applicable Open Source License: Apache 2.0
#
#  NOTE: Cloudera open source products are modular software products
#  made up of hundreds of individual components, each of which was
#  individually copyrighted.  Each Cloudera open source product is a
#  collective work under U.S. Copyright Law. Your license to use the
#  collective work is as provided in your written agreement with
#  Cloudera.  Used apart from the collective work, this file is
#  licensed for your use pursuant to the open source license
#  identified above.
#
#  This code is provided to you pursuant a written agreement with
#  (i) Cloudera, Inc. or (ii) a third-party authorized to distribute
#  this code. If you do not have a written agreement with Cloudera nor
#  with an authorized and properly licensed third party, you do not
#  have any rights to access nor to use this code.
#
#  Absent a written agreement with Cloudera, Inc. (“Cloudera”) to the
#  contrary, A) CLOUDERA PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY
#  KIND; (B) CLOUDERA DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED
#  WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT LIMITED TO
#  IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND
#  FITNESS FOR A PARTICULAR PURPOSE; (C) CLOUDERA IS NOT LIABLE TO YOU,
#  AND WILL NOT DEFEND, INDEMNIFY, NOR HOLD YOU HARMLESS FOR ANY CLAIMS
#  ARISING FROM OR RELATED TO THE CODE; AND (D)WITH RESPECT TO YOUR EXERCISE
#  OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, CLOUDERA IS NOT LIABLE FOR ANY
#  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR
#  CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO, DAMAGES
#  RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF
#  BUSINESS ADVANTAGE OR UNAVAILABILITY, OR LOSS OR CORRUPTION OF
#  DATA.
# ##############################################################################

import os
import pathlib
import uuid
from collections.abc import Iterator

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

from app.main import app


@pytest.fixture
def aws_region() -> str:
    return os.environ.get("AWS_DEFAULT_REGION", "us-west-2")


@pytest.fixture
def s3(
    monkeypatch: pytest.MonkeyPatch,
    aws_region: str,
) -> Iterator["s3.ServiceResource"]:
    """Mock all S3 interactions."""
    monkeypatch.setenv("AWS_DEFAULT_REGION", aws_region)

    config = {
        "core": {
            "mock_credentials": False,
            "passthrough": {
                "urls": [
                    rf"https://bedrock-runtime\.{aws_region}\.amazonaws\.com/model/.*/invoke",
                ],
            },
        }
    }

    with mock_aws(config=config):
        yield boto3.resource("s3")


@pytest.fixture
def document_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def s3_object(
    s3: "s3.ServiceResource", aws_region: str, document_id: str
) -> "s3.Object":
    """Put and return a mocked S3 object"""
    bucket_name = "test_bucket"
    key = "test/" + document_id

    bucket = s3.Bucket(bucket_name)
    bucket.create(CreateBucketConfiguration={"LocationConstraint": aws_region})
    return bucket.put_object(
        Key=key,
        # TODO: fixturize file
        Body=b"test",
        Metadata={"originalfilename": "test.txt"},
    )


@pytest.fixture
def client(
    monkeypatch: pytest.MonkeyPatch,
    s3: "s3.ServiceResource",
    tmp_path: pathlib.Path,
) -> Iterator[TestClient]:
    """Return a test client for making calls to the service.

    https://www.starlette.io/testclient/

    """
    databases_dir = str(tmp_path / "databases")
    monkeypatch.setenv("RAG_DATABASES_DIR", databases_dir)

    # with monkeypatch.context() as m:
    #     # service isn't pip-installable, so we have to import it
    #     m.syspath_prepend(
    #         os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."),
    #     )
    #     from app.main import app

    with TestClient(app) as test_client:
        yield test_client
