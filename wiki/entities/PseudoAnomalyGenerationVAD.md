---
title: "PseudoAnomalyGenerationVAD"
type: entity
tags: [方法, 视频异常检测, 伪异常]
sources: ["raw/09-archive/Rai et al. - 2024 - Video Anomaly Detection via Spatio-Temporal Pseudo-Anomaly Generation  A Unified Approach.pdf"]
last_updated: 2026-04-20
---

## 定义
PseudoAnomalyGenerationVAD 是一种统一生成时空伪异常并结合多信号评分的视频异常检测方法实体。

## 关键信息
- 用 latent diffusion model 生成空间伪异常，用光流 mixup 生成时间伪异常。
- 检测阶段统一聚合重建质量、时间不规则性与语义不一致性三类指标。
- 其核心价值在于尽量构造更贴近开放集真实异常边界的近异常样本。

## 关联连接
- [[PseudoAnomalyGeneration]] — 核心概念。
- [[VideoAnomalyDetection]] — 所属任务。
- [[摘要-video-anomaly-detection-via-spatio-temporal-pseudo-anomaly-generation-a-unified-approach]] — 来源论文。
