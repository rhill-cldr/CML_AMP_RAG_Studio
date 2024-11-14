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
from typing import Any, Sequence, List, Optional, Union, Dict

import httpx
from llama_index.core.base.llms.generic_utils import chat_to_completion_decorator
from llama_index.core.base.llms.types import LLMMetadata, CompletionResponseAsyncGen, ChatMessage, ChatResponseAsyncGen, \
    CompletionResponse, ChatResponse, CompletionResponseGen, ChatResponseGen, MessageRole
from llama_index.core.constants import DEFAULT_TEMPERATURE
from llama_index.core.llms.function_calling import FunctionCallingLLM
from llama_index.llms.mistralai.base import to_mistral_chatmessage, DEFAULT_MISTRALAI_MAX_TOKENS, \
    DEFAULT_MISTRALAI_MODEL
from llama_index.llms.openai import OpenAI
from mistralai import Mistral
from llama_index.core.bridge.pydantic import Field, PrivateAttr


class CaiiModel(OpenAI):
    context: int = Field(
        description="The context size",
        gt=0,
    )

    def __init__(
            self,
            model: str,
            context: int,
            api_base: str,
            messages_to_prompt,
            completion_to_prompt,
            default_headers):
        super().__init__(
            model=model,
            api_base=api_base,
            messages_to_prompt=messages_to_prompt,
            completion_to_prompt=completion_to_prompt,
            default_headers=default_headers)
        self.context = context

    @property
    def metadata(self) -> LLMMetadata:
        ## todo: pull this info from somewhere
        return LLMMetadata(
            context_window=self.context,
            num_output=self.max_tokens or -1,
            is_chat_model=True,
            is_function_calling_model=True,
            model_name=self.model,
        )


class CaiiModelMistral(FunctionCallingLLM):

    context: int = Field(
        description="The context size",
        gt=0,
    )
    _client: Mistral = PrivateAttr()
    max_tokens: int = Field(
        default=DEFAULT_MISTRALAI_MAX_TOKENS,
        description="The maximum number of tokens to generate.",
        gt=0,
    )
    model: str = Field(
        default=DEFAULT_MISTRALAI_MODEL, description="The mistralai model to use."
    )
    temperature: float = Field(
        default=DEFAULT_TEMPERATURE,
        description="The temperature to use for sampling.",
        gte=0.0,
        lte=1.0,
    )
    random_seed: str = Field(
        default=None, description="The random seed to use for sampling."
    )
    additional_kwargs: Dict[str, Any] = Field(
        default_factory=dict, description="Additional kwargs for the MistralAI API."
    )
    timeout: float = Field(
        default=120, description="The timeout to use in seconds.", gte=0
    )
    max_retries: int = Field(
        default=5, description="The maximum number of API retries.", gte=0
    )


    def __init__(
            self,
            model: str,
            context: int,
            api_base: str,
            messages_to_prompt,
            completion_to_prompt,
            default_headers):
        super().__init__(
            context=context,
            api_key="test",
            model=model,
            endpoint=api_base,
            messages_to_prompt=messages_to_prompt,
            completion_to_prompt=completion_to_prompt)
        self.context = context
        httpx_client=  httpx.Client(headers=default_headers)
        self._client = Mistral(api_key="test", server_url=api_base, client=httpx_client)

    @classmethod
    def class_name(cls) -> str:
        return "Custom_MistralAI_LLM"

    @property
    def _model_kwargs(self) -> Dict[str, Any]:
        base_kwargs = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "random_seed": self.random_seed,
            "retries": self.max_retries,
            "timeout_ms": self.timeout * 1000,
        }
        return {
            **base_kwargs,
            **self.additional_kwargs,
        }

    def _get_all_kwargs(self, **kwargs: Any) -> Dict[str, Any]:
        return {
            **self._model_kwargs,
            **kwargs,
        }

    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        messages = to_mistral_chatmessage(messages)
        all_kwargs = self._get_all_kwargs(**kwargs)
        response = self._client.chat.complete(messages=messages, **all_kwargs)

        tool_calls = response.choices[0].message.tool_calls

        return ChatResponse(
            message=ChatMessage(
                role=MessageRole.ASSISTANT,
                content=response.choices[0].message.content,
                additional_kwargs=(
                    {"tool_calls": tool_calls} if tool_calls is not None else {}
                ),
            ),
            raw=dict(response),
        )

    @property
    def metadata(self) -> LLMMetadata:
        ## todo: pull this info from somewhere
        return LLMMetadata(
            context_window=self.context,
            num_output=self.max_tokens or -1,
            is_chat_model=True,
            is_function_calling_model=True,
            model_name=self.model,
        )

    def complete(self, prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponse:
        complete_fn = chat_to_completion_decorator(self.chat)
        return complete_fn(prompt, **kwargs)

    def stream_chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponseGen:
        pass

    def stream_complete(self, prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponseGen:
        pass

    async def achat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        pass

    async def acomplete(self, prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponse:
        pass

    async def astream_chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponseAsyncGen:
        pass

    async def astream_complete(self, prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponseAsyncGen:
        pass


    def _prepare_chat_with_tools(self, tools: List["BaseTool"], user_msg: Optional[Union[str, ChatMessage]] = None,
                                 chat_history: Optional[List[ChatMessage]] = None, verbose: bool = False,
                                 allow_parallel_tool_calls: bool = False, **kwargs: Any) -> Dict[str, Any]:
        pass


