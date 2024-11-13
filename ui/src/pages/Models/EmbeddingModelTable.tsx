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

import { Button, Table, TableProps } from "antd";
import { Model, useTestEmbeddingModel } from "src/api/modelsApi.ts";
import { useState } from "react";

const columns = (
  testModel: (model_id: string) => void,
): TableProps<Model>["columns"] => [
  {
    title: "Model ID",
    dataIndex: "model_id",
    key: "model_id",
    width: 180,
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
      return available ? "Available" : "Unavailable";
    },
  },
  {
    title: "Test",
    key: "test",
    render: (_, { model_id, available }) => {
      return (
        <Button
          onClick={() => {
            testModel(model_id);
          }}
          disabled={available != undefined && !available}
        >
          Test
        </Button>
      );
    },
  },
];

const EmbeddingModelTable = ({
  embeddingModels,
  areEmbeddingModelsLoading,
}: {
  embeddingModels?: Model[];
  areEmbeddingModelsLoading: boolean;
}) => {
  const [model_id, setModelId] = useState<string | undefined>(undefined);
  const { data } = useTestEmbeddingModel(model_id ?? "");
  const [testedModelIds, setTestedModelIds] =
    useState<Record<string, boolean>>();
  console.log(data);
  const testModel = (model_id: string) => {
    setModelId(model_id);
    console.log(`Testing model with id: ${model_id}`);
  };

  return (
    <Table
      dataSource={embeddingModels}
      columns={columns(testModel)}
      style={{ width: "100%" }}
      loading={areEmbeddingModelsLoading}
    />
  );
};

export default EmbeddingModelTable;
