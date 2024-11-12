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

import json

from llama_index.core.base.embeddings.base import BaseEmbedding, Embedding
from openai import OpenAI
from pydantic import Field


class CaiiEmbeddingModel(BaseEmbedding):
    endpoint = Field(any, description="The endpoint to use for embeddings")

    def __init__(self, endpoint):
        super().__init__()
        self.endpoint = endpoint

    def _get_text_embedding(self, text: str) -> Embedding:
        return self._get_embedding(text, "passage")

    async def _aget_query_embedding(self, query: str) -> Embedding:
        pass

    def _get_query_embedding(self, query: str) -> Embedding:
        return self._get_embedding(query, "query")

    def _get_embedding(self, query: str, input_type: str) -> Embedding:
        client, model = self._get_client()
        query = query.replace("\n", " ")
        return (
            client.embeddings.create(input=[query], extra_body={ "input_type": input_type, "truncate": "END"}, model=model).data[0].embedding
        )

    def _get_client(self) -> (OpenAI, any):
        api_base = self.endpoint["url"].removesuffix("/embeddings")

        with open('/tmp/jwt', 'r') as file:
            jwt_contents = json.load(file)
        access_token = jwt_contents['access_token']
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return  OpenAI(base_url=api_base, default_headers=headers, api_key="api_key"), self.endpoint["endpointmetadata"]["model_name"]