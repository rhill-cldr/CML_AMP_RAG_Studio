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

"""Integration tests for app/routers/index/data_source/."""

from typing import Any

from llama_index.core import VectorStoreIndex
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import qdrant_client

from app.services.qdrant import table_name_from, create_qdrant_clients
from app.services import models

def get_vector_store_index(data_source_id) -> VectorStoreIndex:
    client = qdrant_client.QdrantClient(host="localhost", port=6333)
    collection_name = f"index_{data_source_id}"
    assert client.collection_exists(collection_name)
    vector_store = QdrantVectorStore(
        table_name_from(data_source_id), *create_qdrant_clients()
    )
    index = VectorStoreIndex.from_vector_store(vector_store, embed_model=models.get_embedding_model())
    return index


class TestDocumentIndexing:

    @staticmethod
    def test_create_document(
            client,
            index_document_request_body: dict[str, Any],
            document_id: str,
            data_source_id: int,
    ) -> None:
        """Test POST /index/download-and-index."""
        response = client.post(
            "/index/download-and-index",
            json=index_document_request_body,
        )

        assert response.status_code == 200
        assert document_id is not None
        index = get_vector_store_index(data_source_id)
        vectors = index.vector_store.query(VectorStoreQuery(query_embedding=[-1] * 1024, doc_ids=[document_id]))
        assert len(vectors.nodes) == 1


    @staticmethod
    def test_delete_data_source(
            client,
            data_source_id: int,
            document_id: str,
            index_document_request_body: dict[str, Any],
    ) -> None:
        """Test DELETE /index/data_sources/{data_source_id}."""
        client.post(
            "/index/download-and-index",
            json=index_document_request_body,
        )

        index = get_vector_store_index(data_source_id)
        vectors = index.vector_store.query(VectorStoreQuery(query_embedding=[-1] * 1024, doc_ids=[document_id]))
        assert len(vectors.nodes) == 1

        response = client.delete(f"/index/data_sources/{data_source_id}")
        assert response.status_code == 200

        q_client = qdrant_client.QdrantClient(host="localhost", port=6333)
        collection_name = f"index_{data_source_id}"
        assert q_client.collection_exists(collection_name) is False

        get_summary_response = client.get(f'/index/data_sources/{data_source_id}/documents/{document_id}/summary')
        assert get_summary_response.status_code == 404


    @staticmethod
    def test_delete_document(
            client,
            data_source_id: int,
            document_id: str,
            index_document_request_body: dict[str, Any],
    ) -> None:
        """Test DELETE /index/data_sources/{data_source_id}/documents/{document_id}."""
        client.post(
            "/index/download-and-index",
            json=index_document_request_body,
        )

        index = get_vector_store_index(data_source_id)
        vectors = index.vector_store.query(VectorStoreQuery(query_embedding=[-1] * 1024, doc_ids=[document_id]))
        assert len(vectors.nodes) == 1

        response = client.delete(f"/index/data_sources/{data_source_id}/documents/{document_id}")
        assert response.status_code == 200

        index = get_vector_store_index(data_source_id)
        vectors = index.vector_store.query(VectorStoreQuery(query_embedding=[-1] * 1024, doc_ids=[document_id]))
        assert len(vectors.nodes) == 0


    @staticmethod
    def test_get_size(
            client,
            data_source_id: int,
            index_document_request_body: dict[str, Any],
    ) -> None:
        """Test GET /index/data_sources/{data_source_id}/size."""
        client.post(
            "/index/download-and-index",
            json=index_document_request_body,
        )

        response = client.get(f"/index/data_sources/{data_source_id}/size")
        assert response.status_code == 200
        assert response.json() == 1
