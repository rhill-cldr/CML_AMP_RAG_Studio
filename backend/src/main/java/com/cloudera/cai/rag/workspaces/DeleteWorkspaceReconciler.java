/*
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
 */

package com.cloudera.cai.rag.workspaces;

import com.cloudera.cai.rag.configuration.JdbiConfiguration;
import com.cloudera.cai.rag.external.RagBackendClient;
import com.cloudera.cai.util.Tracker;
import com.cloudera.cai.util.reconcilers.*;
import io.opentelemetry.api.OpenTelemetry;
import java.util.Set;
import lombok.extern.slf4j.Slf4j;
import org.jdbi.v3.core.Jdbi;
import org.springframework.stereotype.Component;

@Component
@Slf4j
public class DeleteWorkspaceReconciler extends BaseReconciler<Long> {
  private final Jdbi jdbi;
  private final RagBackendClient ragBackendClient;

  public DeleteWorkspaceReconciler(
      Jdbi jdbi,
      RagBackendClient ragBackendClient,
      ReconcilerConfig reconcilerConfig,
      OpenTelemetry openTelemetry) {
    super(reconcilerConfig, openTelemetry);
    this.jdbi = jdbi;
    this.ragBackendClient = ragBackendClient;
  }

  @Override
  public void resync() {
    log.debug("Checking for workspaces to delete");
    jdbi.useHandle(
        handle ->
            handle
                .createQuery("SELECT id FROM WORKSPACE WHERE deleted IS NOT NULL")
                .mapTo(Long.class)
                .forEach(this::submit));
  }

  @Override
  public ReconcileResult reconcile(Set<Long> workspaceIds) {
    for (Long workspaceId : workspaceIds) {
      log.info("telling the rag backend to delete workspace with id: {}", workspaceId);
      ragBackendClient.deleteWorkspace(workspaceId);
      log.info("deleting workspace from the database: {}", workspaceId);
      jdbi.useTransaction(
          handle -> {
            handle.execute("DELETE FROM WORKSPACE WHERE ID = ?", workspaceId);
            handle.execute("DELETE FROM WORKSPACE_DATA_SOURCE WHERE WORKSPACE_ID = ?", workspaceId);
          });
    }
    return new ReconcileResult();
  }

  // nullables stuff below here
  public static DeleteWorkspaceReconciler createNull(
      Tracker<RagBackendClient.TrackedRequest<?>> tracker) {
    return new DeleteWorkspaceReconciler(
        JdbiConfiguration.createNull(),
        RagBackendClient.createNull(tracker),
        ReconcilerConfig.builder().isTestReconciler(true).build(),
        OpenTelemetry.noop());
  }
}
