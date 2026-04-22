---
title: "VADMamba"
type: entity
tags: [方法, 视频异常检测, 状态空间模型]
sources: ["raw/09-archive/Lyu et al. - 2025 - VADMamba Exploring State Space Models for Fast Video Anomaly Detection.pdf"]
last_updated: 2026-04-20
---

## 定义
VADMamba 是把 Mamba 状态空间模型引入视频异常检测、并强调高效推理的无监督混合检测方法实体。

## 关键信息
- 以 VQ-MaU 为核心结构，把状态空间模型用于视频时序建模。
- 同时执行未来帧预测与光流重建，再用 clip-level fusion evaluation 选择更可靠的异常分数来源。
- 代表了“高效长序列建模”进入 VAD 的一条清晰技术路线。

## 关联连接
- [[StateSpaceModel]] — 核心上位概念。
- [[VideoAnomalyDetection]] — 所属任务。
- [[摘要-vadmamba-exploring-state-space-models-for-fast-video-anomaly-detection]] — 来源论文。
