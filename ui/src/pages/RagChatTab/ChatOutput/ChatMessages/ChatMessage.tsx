/*******************************************************************************
 * CLOUDERA APPLIED MACHINE LEARNING PROTOTYPE (AMP)
 * (C) Cloudera, Inc. 2024
 * All rights reserved.
 *
 * Applicable Open Source License: Apache 2.0
 *
 * NOTE: Cloudera open source products are modular software products
 * made up of hundreds of individual components, each of which was
 * individually copyrighted.  Each Cloudera open source product is a
 * collective work under U.S. Copyright Law. Your license to use the
 * collective work is as provided in your written agreement with
 * Cloudera.  Used apart from the collective work, this file is
 * licensed for your use pursuant to the open source license
 * identified above.
 *
 * This code is provided to you pursuant a written agreement with
 * (i) Cloudera, Inc. or (ii) a third-party authorized to distribute
 * this code. If you do not have a written agreement with Cloudera nor
 * with an authorized and properly licensed third party, you do not
 * have any rights to access nor to use this code.
 *
 * Absent a written agreement with Cloudera, Inc. (“Cloudera”) to the
 * contrary, A) CLOUDERA PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY
 * KIND; (B) CLOUDERA DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED
 * WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT LIMITED TO
 * IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND
 * FITNESS FOR A PARTICULAR PURPOSE; (C) CLOUDERA IS NOT LIABLE TO YOU,
 * AND WILL NOT DEFEND, INDEMNIFY, NOR HOLD YOU HARMLESS FOR ANY CLAIMS
 * ARISING FROM OR RELATED TO THE CODE; AND (D)WITH RESPECT TO YOUR EXERCISE
 * OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, CLOUDERA IS NOT LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR
 * CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO, DAMAGES
 * RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF
 * BUSINESS ADVANTAGE OR UNAVAILABILITY, OR LOSS OR CORRUPTION OF
 * DATA.
 ******************************************************************************/

import { Divider, Flex, Typography } from "antd";
import SourceNodes from "pages/RagChatTab/ChatOutput/Sources/SourceNodes.tsx";
import PendingRagOutputSkeleton from "pages/RagChatTab/ChatOutput/Loaders/PendingRagOutputSkeleton.tsx";
import { ChatMessageType, isPlaceholder } from "src/api/chatApi.ts";
import { cdlBlue500 } from "src/cuix/variables.ts";
import UserQuestion from "pages/RagChatTab/ChatOutput/ChatMessages/UserQuestion.tsx";
import { Evaluations } from "pages/RagChatTab/ChatOutput/ChatMessages/Evaluations.tsx";
import Images from "src/components/images/Images.ts";

const ChatMessage = ({
  data,
  isLast,
}: {
  data: ChatMessageType;
  isLast: boolean;
}) => {
  if (isPlaceholder(data)) {
    return <PendingRagOutputSkeleton question={data.rag_message.user} />;
  }

  return (
    <div data-testid="chat-message">
      {data.rag_message.user ? (
        <div>
          <UserQuestion question={data.rag_message.user} />
          <Flex
            style={{ marginTop: 15 }}
            align="baseline"
            justify="space-between"
            gap={8}
          >
            <div style={{ flex: 1 }}>
              <Images.AiAssistantWhite
                style={{
                  padding: 4,
                  backgroundColor: cdlBlue500,
                  borderRadius: 20,
                  width: 24,
                  height: 24,
                  flex: 1,
                }}
              />
            </div>
            <Flex vertical gap={12} style={{ width: "100%" }}>
              <SourceNodes data={data} />
              <Typography.Text style={{ fontSize: 16, whiteSpace: "pre-wrap" }}>
                {data.rag_message.assistant}
              </Typography.Text>
              <Evaluations evaluations={data.evaluations} />
            </Flex>
          </Flex>
        </div>
      ) : null}
      {isLast ? null : <Divider />}
    </div>
  );
};

export default ChatMessage;
