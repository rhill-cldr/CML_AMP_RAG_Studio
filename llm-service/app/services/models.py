#
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
#  Absent a written agreement with Cloudera, Inc. ("Cloudera") to the
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
#
import os
from enum import Enum
from typing import Literal

from fastapi import HTTPException
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.llms import LLM
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.llms.bedrock import Bedrock

from .caii import get_caii_embedding_models, get_caii_llm_models
from .caii import get_embedding_model as caii_embedding
from .caii import get_llm as caii_llm
from .llama_utils import completion_to_prompt, messages_to_prompt


def get_embedding_model() -> BaseEmbedding:
    if "CAII_DOMAIN" in os.environ:
        return caii_embedding()
    return BedrockEmbedding(model_name="cohere.embed-english-v3")


def get_llm(model_name: str = None) -> LLM:
    if "CAII_DOMAIN" in os.environ:
        return caii_llm(
            domain=os.environ["CAII_DOMAIN"],
            endpoint_name=os.environ["CAII_INFERENCE_ENDPOINT_NAME"],
            messages_to_prompt=messages_to_prompt,
            completion_to_prompt=completion_to_prompt,
        )
    return Bedrock(
        model=model_name,
        context_size=128000,
        messages_to_prompt=messages_to_prompt,
        completion_to_prompt=completion_to_prompt,
    )


def get_available_embedding_models():
    if "CAII_DOMAIN" in os.environ:
        return get_caii_embedding_models()
    return _get_bedrock_embedding_models()


def get_available_llm_models():
    if "CAII_DOMAIN" in os.environ:
        return get_caii_llm_models()
    return _get_bedrock_llm_models()


def _get_bedrock_llm_models():
    return [
        {
            "model_id": "Llama31-8bInstructV1",
            "name": "Llama3.1 8B Instruct v1",
        },
        {
            "model_id": "Llama31-70bInstructV1",
            "name": "Llama3.1 70B Instruct v1",
        },
        {
            "model_id": "Llama31-405bInstructV1",
            "name": "Llama3.1 405B Instruct v1",
        },
    ]


def _get_bedrock_embedding_models():
    return [
        {
            "model_id": "cohere.embed-english-v3",
            "name": "cohere.embed-english-v3",
        }
    ]


class ModelSource(str, Enum):
    BEDROCK = "Bedrock"
    CAII = "CAII"


def get_model_source() -> ModelSource:
    if "CAII_DOMAIN" in os.environ:
        return ModelSource.CAII
    return ModelSource.BEDROCK


def test_llm_model(model_name: str) -> Literal["ok"]:
    models = get_available_llm_models()
    for model in models:
        if model["model_id"] == model_name:
            if model["available"]:
                get_llm(model_name).complete("Are you available to answer questions?")
                return "ok"
            else:
                raise HTTPException(status_code=503, detail="Model unavailable")

    raise HTTPException(status_code=404, detail="Model not found")


def test_embedding_model(model_name: str) -> Literal["ok"]:
    models = get_available_embedding_models()
    for model in models:
        if model["model_id"] == model_name:
            print(f"{model=}")  # TODO: remove this after we're done debugging
            if model["available"]:  # TODO: KeyError here!!!
                # NOTE: when we make embedding models configurable, pass the name to get_embedding_model()
                get_embedding_model().get_text_embedding("Embed this")
                return "ok"
            else:
                raise HTTPException(status_code=503, detail="Model unavailable")

    raise HTTPException(status_code=404, detail="Model not found")

    return "ok"
