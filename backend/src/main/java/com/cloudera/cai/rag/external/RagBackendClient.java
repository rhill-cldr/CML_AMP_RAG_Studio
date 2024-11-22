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

package com.cloudera.cai.rag.external;

import com.cloudera.cai.rag.Types;
import com.cloudera.cai.rag.configuration.AppConfiguration;
import com.cloudera.cai.util.SimpleHttpClient;
import com.cloudera.cai.util.Tracker;
import com.fasterxml.jackson.annotation.JsonProperty;
import io.opentelemetry.instrumentation.annotations.WithSpan;
import java.io.IOException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Component
public class RagBackendClient {
  private final SimpleHttpClient client;
  private final String indexUrl;

  @Autowired
  public RagBackendClient(SimpleHttpClient client) {
    this.client = client;
    indexUrl = AppConfiguration.getRagIndexUrl();
  }

  @WithSpan
  public void indexFile(
      Types.RagDocument ragDocument, String bucketName, IndexConfiguration configuration) {
    try {
      client.post(
          indexUrl
              + "/data_sources/"
              + ragDocument.dataSourceId()
              + "/documents/download-and-index",
          new IndexRequest(bucketName, ragDocument.s3Path(), configuration));
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public String createSummary(Types.RagDocument ragDocument, String bucketName) {
    try {
      return client.post(
          indexUrl + "/data_sources/" + ragDocument.dataSourceId() + "/summarize-document",
          new SummaryRequest(bucketName, ragDocument.s3Path()));
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public void deleteDataSource(Long dataSourceId) {
    client.delete(indexUrl + "/data_sources/" + dataSourceId);
  }

  public void deleteDocument(long dataSourceId, String documentId) {
    client.delete(indexUrl + "/data_sources/" + dataSourceId + "/documents/" + documentId);
  }

  public void deleteSession(Long sessionId) {
    client.delete(indexUrl + "/sessions/" + sessionId);
  }

  public void deleteWorkspace(Long workspaceId) {
    client.delete(indexUrl + "/workspaces/" + workspaceId);
  }

  record IndexRequest(
      @JsonProperty("s3_bucket_name") String s3BucketName,
      @JsonProperty("s3_document_key") String s3DocumentKey,
      IndexConfiguration configuration) {}

  public record SummaryRequest(
      @JsonProperty("s3_bucket_name") String s3BucketName,
      @JsonProperty("s3_document_key") String s3DocumentKey) {}

  public record IndexConfiguration(
      @JsonProperty("chunk_size") int chunkSize,
      @JsonProperty("chunk_overlap") int chunkOverlapPercentage) {}

  // nullables below here

  public static RagBackendClient createNull() {
    return createNull(new Tracker<>());
  }

  public static RagBackendClient createNull(
      Tracker<TrackedRequest<?>> tracker, RuntimeException... t) {
    return new RagBackendClient(SimpleHttpClient.createNull()) {
      private final RuntimeException[] exceptions = t;
      private int exceptionIndex = 0;

      @Override
      public void indexFile(
          Types.RagDocument ragDocument, String bucketName, IndexConfiguration configuration) {
        super.indexFile(ragDocument, bucketName, configuration);
        tracker.track(
            new TrackedRequest<>(
                new TrackedIndexRequest(
                    bucketName, ragDocument.s3Path(), ragDocument.dataSourceId(), configuration)));
        checkForException();
      }

      private void checkForException() {
        if (exceptionIndex < exceptions.length) {
          throw exceptions[exceptionIndex++];
        }
      }

      @Override
      public void deleteDataSource(Long dataSourceId) {
        super.deleteDataSource(dataSourceId);
        tracker.track(new TrackedRequest<>(new TrackedDeleteDataSourceRequest(dataSourceId)));
        checkForException();
      }

      @Override
      public String createSummary(Types.RagDocument ragDocument, String bucketName) {
        String result = super.createSummary(ragDocument, bucketName);
        tracker.track(new TrackedRequest<>(new SummaryRequest(bucketName, ragDocument.s3Path())));
        checkForException();
        return result;
      }

      @Override
      public void deleteSession(Long sessionId) {
        super.deleteSession(sessionId);
        tracker.track(new TrackedRequest<>(new TrackedDeleteSessionRequest(sessionId)));
        checkForException();
      }

      @Override
      public void deleteWorkspace(Long workspaceId) {
        super.deleteWorkspace(workspaceId);
        tracker.track(new TrackedRequest<>(new TrackedDeleteWorkspaceRequest(workspaceId)));
        checkForException();
      }

      @Override
      public void deleteDocument(long dataSourceId, String documentId) {
        super.deleteDocument(dataSourceId, documentId);
        tracker.track(
            new TrackedRequest<>(new TrackedDeleteDocumentRequest(dataSourceId, documentId)));
        checkForException();
      }
    };
  }

  public record TrackedIndexRequest(
      String bucketName, String s3Path, long dataSourceId, IndexConfiguration configuration) {}

  public record TrackedDeleteSessionRequest(Long sessionId) {}

  public record TrackedDeleteWorkspaceRequest(Long workspaceId) {}

  public record TrackedDeleteDataSourceRequest(long dataSourceId) {}

  public record TrackedRequest<T>(T detail) {}

  public record TrackedDeleteDocumentRequest(long dataSourceId, String documentId) {}
}
