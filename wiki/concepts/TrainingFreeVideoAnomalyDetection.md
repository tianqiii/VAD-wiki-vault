---
title: "TrainingFreeVideoAnomalyDetection"
type: concept
tags: [训练自由, 视频异常检测, 零训练]
sources: ["raw/09-archive/Ahn et al. - 2024 - VideoPatchCore An Effective Method to Memorize Normality for Video Anomaly Detection.pdf", "raw/09-archive/Shao et al. - 2025 - EventVAD training-free event-aware video anomaly detection.pdf"]
last_updated: 2026-04-20
---

## 定义
TrainingFreeVideoAnomalyDetection 指不针对目标数据集进行专门训练，而是依赖预训练特征、检索机制或大模型推理直接完成视频异常检测的路线。

## 关键信息
- 这一路线关注快速部署与低适配成本，但通常需要更强的先验特征或更稳的推理流程。
- VideoPatchCore 代表记忆检索式训练自由方法，EventVAD 代表“先切事件、再做大模型推理”的训练自由方法。
- 训练自由并不等于无结构，事件切分、记忆压缩等前处理反而决定了效果上限。

## 关联连接
- [[VideoPatchCore]] — 记忆增强式训练自由路线。
- [[EventVAD]] — 事件感知大模型路线。
- [[MultimodalVideoAnomalyDetection]] — EventVAD 同时利用多源信号。
- [[VideoAnomalyDetection]] — 所属任务。
