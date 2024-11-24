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
from typing import List, Literal

from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.storage.chat_store import SimpleChatStore
from pydantic import BaseModel

from ..config import settings


class RagPredictSourceNode(BaseModel):
    node_id: str
    doc_id: str
    source_file_name: str
    score: float


class Evaluation(BaseModel):
    name: Literal["relevance", "faithfulness"]
    value: float


class RagContext(BaseModel):
    role: MessageRole
    content: str


class RagStudioChatMessage(BaseModel):
    id: str
    source_nodes: list[RagPredictSourceNode]
    rag_message: dict[Literal["user", "assistant"], str]
    evaluations: list[Evaluation]
    timestamp: float


class ChatHistoryManager:
    def __init__(self, store_path: str):
        self.store_path = store_path

    # note: needs pagination in the future
    def retrieve_chat_history(self, session_id: int) -> List[RagStudioChatMessage]:
        store = self.store_for_session(session_id)

        messages: list[ChatMessage] = store.get_messages(
            self.build_chat_key(session_id)
        )
        results: list[RagStudioChatMessage] = []

        i = 0
        while i < len(messages):
            user_message = messages[i]
            # todo: handle the possibility of falling off the end of the list.
            assistant_message = messages[i + 1]
            # if we are somehow in a bad state, correct it with an empty assistant message and back up the index by one
            if assistant_message.role == MessageRole.USER:
                assistant_message = ChatMessage()
                assistant_message.role = MessageRole.ASSISTANT
                assistant_message.content = ""
                i = i - 1
            results.append(
                RagStudioChatMessage(
                    id=user_message.additional_kwargs["id"],
                    source_nodes=assistant_message.additional_kwargs.get(
                        "source_nodes", []
                    ),
                    rag_message={
                        MessageRole.USER.value: str(user_message.content),
                        MessageRole.ASSISTANT.value: str(assistant_message.content),
                    },
                    evaluations=assistant_message.additional_kwargs.get(
                        "evaluations", []
                    ),
                    timestamp=assistant_message.additional_kwargs.get("timestamp", 0.0),
                )
            )
            i += 2

        return results

    def store_for_session(self, session_id: int) -> SimpleChatStore:
        store = SimpleChatStore.from_persist_path(
            persist_path=self.store_file(session_id)
        )
        return store

    def clear_chat_history(self, session_id: int) -> None:
        store = self.store_for_session(session_id)
        store.delete_messages(self.build_chat_key(session_id))
        store.persist(self.store_file(session_id))

    def delete_chat_history(self, session_id: int) -> None:
        session_storage = self.store_file(session_id)
        if os.path.exists(session_storage):
            os.remove(session_storage)

    def store_file(self, session_id: int) -> str:
        return os.path.join(self.store_path, f"chat_store-{session_id}.json")

    def append_to_history(
        self, session_id: int, messages: List[RagStudioChatMessage]
    ) -> None:
        store = self.store_for_session(session_id)

        for message in messages:
            store.add_message(
                self.build_chat_key(session_id),
                ChatMessage(
                    role=MessageRole.USER,
                    content=message.rag_message["user"],
                    additional_kwargs={
                        "id": message.id,
                    },
                ),
            )
            store.add_message(
                self.build_chat_key(session_id),
                ChatMessage(
                    role=MessageRole.ASSISTANT,
                    content=message.rag_message["assistant"],
                    additional_kwargs={
                        "id": message.id,
                        "source_nodes": message.source_nodes,
                        "evaluations": message.evaluations,
                        "timestamp": message.timestamp,
                    },
                ),
            )
            store.persist(self.store_file(session_id))

    @staticmethod
    def build_chat_key(session_id: int) -> str:
        return "session_" + str(session_id)


chat_store = ChatHistoryManager(store_path=settings.rag_databases_dir)
