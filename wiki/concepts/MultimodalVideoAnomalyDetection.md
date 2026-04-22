---
title: "MultimodalVideoAnomalyDetection"
type: concept
tags: [多模态, 视频异常检测, 音视频]
sources: ["raw/09-archive/Paulraj and Vairavasundaram - 2024 - M 2 VAD  Multiview multimodality transformer-based weakly supervised video anomaly detection.pdf", "raw/09-archive/Shao et al. - 2025 - EventVAD training-free event-aware video anomaly detection.pdf"]
last_updated: 2026-04-20
---

## 定义
MultimodalVideoAnomalyDetection 指同时利用视频、音频、光流、文本或大模型推理等多种信号来提升异常覆盖与判别稳定性的视频异常检测路线。

## 关键信息
- 多模态的价值在于补足单一视觉线索对复杂监控事件的覆盖不足。
- M2VAD 代表音视频与多视角联合建模；EventVAD 则展示了视觉、光流与 MLLM 组合的事件级推理路线。
- 后续应注意区分“音视频多模态”和“视觉+语言推理增强”这两类不同技术形态。

## 关联连接
- [[M2VAD]] — 弱监督音视频多视角路线。
- [[EventVAD]] — 事件级多源推理路线。
- [[WeaklySupervisedVideoAnomalyDetection]] — M2VAD 所属设定。
- [[TrainingFreeVideoAnomalyDetection]] — EventVAD 所属设定。
