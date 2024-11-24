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
 * Absent a written agreement with Cloudera, Inc. ("Cloudera") to the
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

import { cleanup, render, screen } from "@testing-library/react";
import { describe, expect, it, vi, afterEach } from "vitest";
import {
  RagChatContext,
  RagChatContextType,
} from "pages/RagChatTab/State/RagChatContext";
import ChatBodyController from "./ChatBodyController";
import { ConnectionType } from "src/api/dataSourceApi.ts";

const testDataSource = {
  id: 1,
  name: "data source name",
  chunkSize: 1,
  totalDocSize: 1,
  documentCount: 1,
  connectionType: ConnectionType.MANUAL,
  chunkOverlapPercent: 0,
};

const testSession = {
  dataSourceIds: [1],
  id: 1,
  name: "session name",
  timeCreated: 123,
  timeUpdated: 123,
  createdById: "1",
  updatedById: "1",
  lastInteractionTime: 123,
};

describe("ChatBodyController", () => {
  vi.mock("@tanstack/react-router", () => ({
    useParams: vi.fn(() => ({ sessionId: "1" })),
    useNavigate: vi.fn(),
  }));

  vi.mock("src/api/ragQueryApi.ts", () => ({
    useSuggestQuestions: vi.fn(() => ({
      data: "Mocked suggested questions",
      isLoading: false,
    })),
  }));

  vi.mock("src/api/summaryApi.ts", () => ({
    useGetDataSourceSummary: vi.fn(() => ({
      data: "Mocked summary data",
      isLoading: false,
    })),
  }));

  afterEach(() => {
    cleanup();
  });

  const renderWithContext = (contextValue: Partial<RagChatContextType>) => {
    const defaultContextValue: RagChatContextType = {
      currentQuestion: "",
      chatHistory: [],
      dataSourceId: undefined,
      dataSourcesStatus: undefined,
      queryConfiguration: {
        top_k: 5,
        model_name: "",
        exclude_knowledge_base: false,
      },
      setQueryConfiguration: () => null,
      setCurrentQuestion: () => null,
      dataSourceSize: null,
      dataSources: [],
      activeSession: undefined,
    };

    return render(
      <RagChatContext.Provider
        value={{ ...defaultContextValue, ...contextValue }}
      >
        <ChatBodyController />
      </RagChatContext.Provider>,
    );
  };

  it("renders NoSessionState when no sessionId and dataSources are available", () => {
    renderWithContext({
      dataSourceId: undefined,
      dataSourcesStatus: undefined,
      dataSourceSize: null,
      dataSources: [],
      activeSession: undefined,
    });

    expect(screen.getByText("No knowledge bases present")).toBeTruthy();
  });

  it("renders ChatLoading when dataSourcesStatus or chatHistoryStatus is pending", () => {
    renderWithContext({
      dataSourcesStatus: "pending",
    });

    expect(screen.getByTestId("chatLoadingSpinner")).toBeTruthy();
  });

  it("renders error message when dataSourcesStatus or chatHistoryStatus is error", () => {
    renderWithContext({
      dataSourcesStatus: "error",
    });

    expect(screen.getByText("We encountered an error")).toBeTruthy();
  });

  it("renders ChatMessageController when chatHistory exists", () => {
    renderWithContext({
      chatHistory: [
        {
          id: "1",
          rag_message: {
            user: "a test question",
            assistant: "a test response",
          },
          source_nodes: [],
          evaluations: [],
          timestamp: 123,
        },
      ],
    });

    expect(screen.getByTestId("chat-message")).toBeTruthy();
  });

  it("renders NoDataSourcesState when no dataSources are available", () => {
    renderWithContext({
      dataSources: [],
      activeSession: testSession,
    });

    expect(
      screen.getByText(
        "In order to get started, create a new knowledge base using the button below.",
      ),
    ).toBeTruthy();
  });

  it("renders NoDataSourceForSession when no currentDataSource is found", () => {
    renderWithContext({
      dataSources: [testDataSource],
      dataSourceId: undefined,
      activeSession: { ...testSession, dataSourceIds: [2] },
    });

    expect(
      screen.getByText("No knowledge base for this session."),
    ).toBeTruthy();
  });

  it("renders ChatMessageController when currentQuestion and dataSourceSize are available", () => {
    renderWithContext({
      currentQuestion: "What is AI?",
      dataSourceSize: 1,
      dataSources: [testDataSource],
      activeSession: testSession,
    });

    expect(screen.getByTestId("chat-message-controller")).toBeTruthy();
  });

  it("renders EmptyChatState when no chatHistory and dataSourceSize is available", () => {
    vi.mock(
      "src/pages/RagChatTab/ChatOutput/Placeholders/EmptyChatState.tsx",
      () => ({
        __esModule: true,
        default: vi.fn(({ dataSourceSize }: { dataSourceSize: number }) => (
          <div data-testid="empty-chat-state">{dataSourceSize}</div>
        )),
      }),
    );

    renderWithContext({
      dataSourceSize: 1,
      dataSources: [testDataSource],
      activeSession: testSession,
    });

    expect(screen.getByTestId("empty-chat-state")).toBeTruthy();
  });
});
