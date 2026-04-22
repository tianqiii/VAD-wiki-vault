---
title: "EventVAD"
type: entity
tags: [方法, 视频异常检测, 训练自由]
sources: ["raw/09-archive/Shao et al. - 2025 - EventVAD training-free event-aware video anomaly detection.pdf"]
last_updated: 2026-04-20
---

## 定义
EventVAD 是一种先做事件边界切分、再让多模态大模型进行层级推理的训练自由视频异常检测方法实体。

## 关键信息
- 先结合 CLIP 特征、RAFT 光流、动态图和图注意力识别长视频中的事件单元。
- 再让 MLLM 在事件级而非逐帧级做推理与评分，以减少长视频异常分数抖动。
- 它说明训练自由方法要想稳定，前置时序结构整理往往比直接逐帧喂大模型更关键。

## 关联连接
- [[TrainingFreeVideoAnomalyDetection]] — 所属设定。
- [[MultimodalVideoAnomalyDetection]] — 使用多源信号与大模型推理。
- [[摘要-eventvad-training-free-event-aware-video-anomaly-detection]] — 来源论文。
