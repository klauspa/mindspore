/**
 * Copyright 2019 Huawei Technologies Co., Ltd
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef MINDSPORE_CCSRC_PARALLEL_OPS_INFO_BIAS_ADD_INFO_H_
#define MINDSPORE_CCSRC_PARALLEL_OPS_INFO_BIAS_ADD_INFO_H_

#include <string>

#include <memory>
#include <unordered_map>
#include <vector>

#include "ir/value.h"
#include "parallel/auto_parallel/operator_costmodel.h"
#include "parallel/ops_info/operator_info.h"
#include "parallel/strategy.h"

namespace mindspore {
namespace parallel {
class BiasAddInfo : public OperatorInfo {
 public:
  BiasAddInfo(const std::string& operator_name, const Shapes& inputs_shape, const Shapes& outputs_shape,
              const PrimitiveAttrs& attrs)
      : OperatorInfo(operator_name, inputs_shape, outputs_shape, attrs, std::make_shared<BiasAddCost>()) {}
  ~BiasAddInfo() override = default;

  Status Init(const StrategyPtr& strategy) override;
  Status InitForCostModel(const StrategyPtr& strategy) override;
  Status GenerateStrategies(int32_t) override;
  Status SetCostUnderStrategy(const StrategyPtr&) override;
  void ReComputeBatchSplitFlagList() override;

 protected:
  Status GetAttrs() override { return SUCCESS; }
  Status CheckStrategy(const StrategyPtr& strategy) override;
  Status InferMirrorOps() override;
  Status InferForwardCommunication() override { return SUCCESS; }
  Status InferTensorInfo() override;
  Status InferDevMatrixShape() override;
  Status InferTensorMap() override;
  Status InferTensorLayout(TensorLayouts* inputs_layout, TensorLayouts* outputs_layout, const Shape& dev_matrix_array);
};
}  // namespace parallel
}  // namespace mindspore

#endif  // MINDSPORE_CCSRC_PARALLEL_OPS_INFO_BIAS_ADD_INFO_H_
