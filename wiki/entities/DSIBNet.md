---
title: "DSIBNet"
type: entity
tags: [方法, 视频异常检测, 轻量化]
sources: ["raw/09-archive/Zhu et al. - 2025 - DS-IB Net Ultra-Lightweight Weakly-Supervised Video Anomaly Detection through Synergistic Dual Stre.pdf"]
last_updated: 2026-04-20
---

## 定义
DSIBNet 是一种面向弱监督视频异常检测的超轻量双流信息瓶颈方法实体。

## 关键信息
- 通过 Information Bottleneck 压缩正常动态中的冗余信息，建立轻量主干。
- 额外引入瞬时外观补偿支路，保留容易被压缩掉的异常细节。
- 用 Adaptive Feature Arbitration 动态调节动态表示权重，在效率与异常敏感性之间折中。

## 关联连接
- [[InformationBottleneck]] — 核心概念。
- [[WeaklySupervisedVideoAnomalyDetection]] — 所属任务设定。
- [[摘要-ds-ib-net-ultra-lightweight-weakly-supervised-video-anomaly-detection-through-synergistic-dual-streams-and-information-bottleneck]] — 来源论文。
