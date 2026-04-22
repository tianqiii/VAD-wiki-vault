---
title: "WeaklySupervisedVideoAnomalyDetection"
type: concept
tags: [弱监督, 视频异常检测, 视频级标签]
sources: ["raw/09-archive/Paulraj and Vairavasundaram - 2024 - M 2 VAD  Multiview multimodality transformer-based weakly supervised video anomaly detection.pdf", "raw/09-archive/Zhu et al. - 2025 - ProDisc-VAD An Efficient System for Weakly-Supervised Anomaly Detection in Video Surveillance Appli.pdf", "raw/09-archive/Zhu et al. - 2025 - DS-IB Net Ultra-Lightweight Weakly-Supervised Video Anomaly Detection through Synergistic Dual Stre.pdf", "raw/09-archive/Yang et al. - 2026 - Attention-driven pseudo-label self-training for weakly supervised video anomaly detection.pdf", "raw/09-archive/Wu et al. - 2024 - VadCLIP Adapting Vision-Language Models for Weakly Supervised Video Anomaly Detection.pdf"]
last_updated: 2026-04-22
---

## 定义
WeaklySupervisedVideoAnomalyDetection 指仅使用视频级或粗粒度标签训练模型，在缺少片段级精确标注的情况下学习异常定位与评分。

## 关键信息
- 核心问题是如何从粗标签中提纯可靠监督信号，避免噪声片段持续误导训练。
- 本库涉及的代表方案包括原型交互、极值伪实例学习、同步式伪标签自训练、多视角多模态融合与轻量双流信息瓶颈。
- 该方向通常在标注成本、性能与部署效率之间寻找折中。
- VadCLIP 代表了另一条“冻结大模型 + 轻量适配器 + 语言-视觉对齐”的路线：在弱监督条件下把文本类别语义引入异常定位。

## 关联连接
- [[PseudoLabelSelfTraining]] — 伪标签提纯是关键子问题。
- [[MultimodalVideoAnomalyDetection]] — 多源证据融合的重要扩展。
- [[VadCLIP]] — 视觉语言对齐增强的弱监督方法。
- [[ProDiscVAD]] — 轻量极值伪实例路线。
- [[M2VAD]] — 多视角多模态路线。
- [[DSIBNet]] — 超轻量双流信息瓶颈路线。
- [[ADPLGVAD]] — 同步式伪标签自训练路线。
