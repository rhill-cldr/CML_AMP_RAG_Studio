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

import { Button, Flex, Table, TableProps, Tooltip } from "antd";
import { Model, useTestLlmModel } from "src/api/modelsApi.ts";
import React, { useState } from "react";
import { CheckCircleOutlined, CloseCircleOutlined } from "@ant-design/icons";
import { cdlGreen600, cdlRed600 } from "src/cuix/variables.ts";

export function TestCell(props: {
  onClick: () => void;
  available?: boolean;
  loading: boolean;
  error: Error | null;
  data: string | undefined;
}) {
  return (
    <Flex gap={8}>
      <Button
        onClick={props.onClick}
        disabled={props.available != undefined && !props.available}
        loading={props.loading}
      >
        Test
      </Button>
      {props.error || (props.data && props.data !== "ok") ? (
        <Tooltip title={props.error?.message ?? "an error occurred"}>
          <CloseCircleOutlined style={{ color: cdlRed600 }} />
        </Tooltip>
      ) : null}
    </Flex>
  );
}

const InferenceModelTestCell = (props: {
  available: boolean | undefined;
  model_id: string;
}) => {
  const [testModel, setTestModel] = useState("");
  const { data, isLoading, error } = useTestLlmModel(testModel);

  const handleTestModel = () => {
    setTestModel(props.model_id);
  };

  if (data === "ok") {
    return <CheckCircleOutlined style={{ color: cdlGreen600 }} />;
  }

  return (
    <TestCell
      onClick={handleTestModel}
      available={props.available}
      loading={isLoading}
      error={error}
      data={data}
    />
  );
};

export interface TestCellProps {
  available: boolean | undefined;
  model_id: string;
}

export const modelColumns = (
  testCell: (props: TestCellProps) => React.JSX.Element,
): TableProps<Model>["columns"] => [
  {
    title: "Model ID",
    dataIndex: "model_id",
    key: "model_id",
  },
  {
    title: "Name",
    dataIndex: "name",
    key: "name",
  },
  {
    title: "Status",
    dataIndex: "available",
    key: "available",
    render: (available?: boolean) => {
      if (available === undefined) {
        return "Unknown";
      }
      return available ? "Available" : "Not Ready";
    },
  },
  {
    title: "Test",
    width: 140,
    render: (_, { model_id, available }) => {
      return testCell({ available, model_id });
    },
  },
];

const InferenceModelTable = ({
  inferenceModels,
  areInferenceModelsLoading,
}: {
  inferenceModels?: Model[];
  areInferenceModelsLoading: boolean;
}) => {
  return (
    <Table
      dataSource={inferenceModels}
      columns={modelColumns(InferenceModelTestCell)}
      style={{ width: "100%" }}
      loading={areInferenceModelsLoading}
      rowKey={(record) => record.model_id}
    />
  );
};

export default InferenceModelTable;
