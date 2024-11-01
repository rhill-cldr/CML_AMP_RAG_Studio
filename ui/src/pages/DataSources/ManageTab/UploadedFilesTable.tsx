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

import { Popover, Table, TableProps, Tooltip } from "antd";
import { useParams } from "@tanstack/react-router";
import { CheckCircleOutlined, LoadingOutlined } from "@ant-design/icons";
import {
  RagDocumentResponseType,
  useGetRagDocuments,
} from "src/api/ragDocumentsApi.ts";
import { bytesConversion } from "src/utils/bytesConversion.ts";
import StatsWidget from "pages/DataSources/ManageTab/StatsWidget.tsx";
import AiAssistantIcon from "@cloudera-internal/cuix-core/icons/react/AiAssistantIcon";
import DocumentationIcon from "@cloudera-internal/cuix-core/icons/react/DocumentationIcon";
import { useGetDocumentSummary } from "src/api/summaryApi.ts";
import { useState } from "react";

function SummaryPopover({
  dataSourceId,
  timestamp,
  docId,
}: {
  dataSourceId: string;
  timestamp: number | null;
  docId: string;
}) {
  const [visible, setVisible] = useState(false);
  const documentSummary = useGetDocumentSummary({
    data_source_id: dataSourceId,
    doc_id: docId,
    queryEnabled: timestamp != null && visible,
  });

  return (
    <Popover
      title="Generated summary"
      content={<div style={{ width: 400 }}>{documentSummary.data}</div>}
      open={visible && documentSummary.isSuccess}
      onOpenChange={setVisible}
    >
      <DocumentationIcon style={{ height: 20, width: 20 }} />
    </Popover>
  );
}

const columns = (
  dataSourceId: string,
): TableProps<RagDocumentResponseType>["columns"] => [
  {
    title: <AiAssistantIcon />,
    dataIndex: "summaryCreationTimestamp",
    key: "summaryCreationTimestamp",
    render: (timestamp: number | null, data) => {
      return timestamp == null ? (
        <LoadingOutlined spin />
      ) : (
        <SummaryPopover
          dataSourceId={dataSourceId}
          docId={data.documentId}
          timestamp={timestamp}
        />
      );
    },
  },
  {
    title: "Filename",
    dataIndex: "filename",
    key: "filename",
    showSorterTooltip: false,
    sorter: (a, b) => a.filename.localeCompare(b.filename),
  },
  {
    title: "Size",
    dataIndex: "sizeInBytes",
    key: "sizeInBytes",
    render: (sizeInBytes: RagDocumentResponseType["sizeInBytes"]) =>
      bytesConversion(sizeInBytes.toString()),
  },
  {
    title: "Extension",
    dataIndex: "extension",
    key: "extension",
  },
  {
    title: "Creation date",
    dataIndex: "timeCreated",
    key: "timeCreated",
    showSorterTooltip: false,
    sorter: (a, b) => {
      return a.timeCreated - b.timeCreated;
    },
    defaultSortOrder: "descend",
    render: (timestamp) => new Date(timestamp * 1000).toLocaleString(),
  },
  {
    title: <Tooltip title="Document indexing complete">Ready</Tooltip>,
    dataIndex: "vectorUploadTimestamp",
    key: "vectorUploadTimestamp",
    render: (timestamp?: number) =>
      timestamp == null ? <LoadingOutlined spin /> : <CheckCircleOutlined />,
  },
];

const UploadedFilesTable = () => {
  const dataSourceId = useParams({
    from: "/_layout/data/_layout-datasources/$dataSourceId",
  }).dataSourceId;
  const getRagDocuments = useGetRagDocuments(dataSourceId);
  const ragDocuments = getRagDocuments.data
    ? getRagDocuments.data.map((doc) => ({ ...doc, key: doc.id }))
    : [];
  const docsLoading = getRagDocuments.isLoading || getRagDocuments.isPending;

  return (
    <>
      <StatsWidget
        ragDocuments={ragDocuments}
        docsLoading={docsLoading}
        dataSourceId={dataSourceId}
      />
      <Table<RagDocumentResponseType>
        loading={docsLoading}
        dataSource={ragDocuments}
        columns={columns(dataSourceId)}
      />
    </>
  );
};

export default UploadedFilesTable;
