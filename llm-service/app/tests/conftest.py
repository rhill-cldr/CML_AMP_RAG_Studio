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
from dataclasses import dataclass
from typing import Any, Dict, Sequence

import boto3
import lipsum
import pytest
import qdrant_client as q_client
from boto3.resources.base import ServiceResource
from fastapi.testclient import TestClient
from llama_index.core.base.embeddings.base import BaseEmbedding, Embedding
from llama_index.core.base.llms.types import (
    ChatMessage,
    ChatResponse,
    ChatResponseAsyncGen,
    ChatResponseGen,
    CompletionResponse,
    CompletionResponseAsyncGen,
    CompletionResponseGen,
    LLMMetadata,
)
from llama_index.core.llms import LLM
from moto import mock_aws
from pydantic import Field

from app.ai.vector_stores.qdrant import QdrantVectorStore
from app.main import app
from app.services import models
from app.services.utils import get_last_segment


@dataclass
class BotoObject:
    bucket_name: str
    key: str


@pytest.fixture
def qdrant_client() -> q_client.QdrantClient:
    return q_client.QdrantClient(":memory:")


@pytest.fixture
def aws_region() -> str:
    return os.environ.get("AWS_DEFAULT_REGION", "us-west-2")


@pytest.fixture(autouse=True)
def databases_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> str:
    databases_dir: str = str(tmp_path / "databases")
    monkeypatch.setenv("RAG_DATABASES_DIR", databases_dir)
    return databases_dir


@pytest.fixture
def s3_client(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[ServiceResource]:
    """Mock all S3 interactions."""

    with mock_aws():
        yield boto3.resource("s3")


@pytest.fixture
def document_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def data_source_id() -> int:
    return -1


@pytest.fixture
def index_document_request_body(
    data_source_id: int, s3_object: BotoObject
) -> Dict[str, Any]:
    return {
        "document_id": get_last_segment(s3_object.key),
        "data_source_id": data_source_id,
        "s3_bucket_name": s3_object.bucket_name,
        "s3_document_key": s3_object.key,
        "configuration": {
            "chunk_size": 512,
            "chunk_overlap": 10,
        },
    }


class DummyLlm(LLM):
    completion_response = Field("this is a completion response")
    chat_response = Field("this is a chat response")

    def __init__(
        self,
        completion_response: str = "this is a completion response",
        chat_response: str = "hello",
    ):
        super().__init__()
        self.completion_response = completion_response
        self.chat_response = chat_response

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata()

    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        return ChatResponse(message=ChatMessage.from_str(self.chat_response))

    def complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        return CompletionResponse(text=self.completion_response)

    def stream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseGen:
        raise NotImplementedError("Not implemented")

    def stream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseGen:
        raise NotImplementedError("Not implemented")

    async def achat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponse:
        raise NotImplementedError("Not implemented")

    async def acomplete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        raise NotImplementedError("Not implemented")

    async def astream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseAsyncGen:
        raise NotImplementedError("Not implemented")

    async def astream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseAsyncGen:
        raise NotImplementedError("Not implemented")


class DummyEmbeddingModel(BaseEmbedding):
    def _get_query_embedding(self, query: str) -> Embedding:
        return [0.1] * 1024

    async def _aget_query_embedding(self, query: str) -> Embedding:
        return [0.1] * 1024

    def _get_text_embedding(self, text: str) -> Embedding:
        return [0.1] * 1024


@pytest.fixture(autouse=True)
def vector_store(
    monkeypatch: pytest.MonkeyPatch, qdrant_client: q_client.QdrantClient
) -> None:
    original = QdrantVectorStore.for_chunks
    monkeypatch.setattr(
        QdrantVectorStore,
        "for_chunks",
        lambda ds_id: original(ds_id, qdrant_client),
    )


@pytest.fixture(autouse=True)
def summary_vector_store(
    monkeypatch: pytest.MonkeyPatch, qdrant_client: q_client.QdrantClient
) -> None:
    original = QdrantVectorStore.for_summaries
    monkeypatch.setattr(
        QdrantVectorStore,
        "for_summaries",
        lambda ds_id: original(ds_id, qdrant_client),
    )


@pytest.fixture(autouse=True)
def embedding_model(monkeypatch: pytest.MonkeyPatch) -> BaseEmbedding:
    model = DummyEmbeddingModel()

    # Requires that the app usages import the file and not the function directly as python creates a copy when importing the function
    monkeypatch.setattr(models, "get_embedding_model", lambda: model)
    return model


@pytest.fixture(autouse=True)
def llm(monkeypatch: pytest.MonkeyPatch) -> LLM:
    model = DummyLlm()

    # Requires that the app usages import the file and not the function directly as python creates a copy when importing the function
    monkeypatch.setattr(models, "get_llm", lambda model_name: model)
    return model


@pytest.fixture
def s3_object(
    s3_client: ServiceResource, aws_region: str, document_id: str
) -> BotoObject:
    """Put and return a mocked S3 object"""
    bucket_name = "test_bucket"
    key = "test/" + document_id

    body = lipsum.generate_words(1000)

    bucket = s3_client.Bucket(bucket_name)
    bucket.create(CreateBucketConfiguration={"LocationConstraint": aws_region})
    bucket.put_object(
        Key=key,
        # TODO: fixturize file
        Body=body.encode("utf-8"),
        Metadata={"originalfilename": "test.txt"},
    )
    return BotoObject(bucket_name=bucket_name, key=key)


@pytest.fixture
def client(
    s3_client: ServiceResource,
) -> Iterator[TestClient]:
    """Return a test client for making calls to the service.

    https://www.starlette.io/testclient/

    """
    with TestClient(app) as test_client:
        yield test_client
