---
title: "摘要-m2vad-multiview-multimodality-transformer-based-weakly-supervised-video-anomaly-detection"
type: source
tags: [来源, 论文, 视频异常检测]
sources: ["raw/09-archive/Paulraj and Vairavasundaram - 2024 - M 2 VAD  Multiview multimodality transformer-based weakly supervised video anomaly detection.pdf"]
last_updated: 2026-04-22
---

## Metadata
- **作者**: Shalmiya Paulraj，Subramaniyaswamy Vairavasundaram
- **年份**: 2024
- **期刊/会议**: Image and Vision Computing
- **DOI / arXiv**: DOI: 10.1016/j.imavis.2024.105139；arXiv: 未在公开信息中找到

## 核心摘要
这篇论文提出了 M2VAD，一个面向弱监督视频异常检测的多视角多模态 Transformer 框架。方法同时处理视频与音频，并通过多视角输入、跨视角注意力以及跨模态同步模块来缓解时序错位和融合低效问题。论文重点强调在复杂监控场景下，仅靠单一模态或单一视角难以稳定覆盖异常证据，因此需要把时空视觉线索与声音信号共同纳入建模。实验显示其在 UCF-Crime、ShanghaiTech 与 XD-Violence 上相对当时基线具有明显优势，但也伴随较高计算复杂度。

## 论文问题
- 在复杂监控场景下，单一模态或单一视角为何不足以稳定覆盖异常证据。
- 如何在弱监督设定下更有效地对齐多视角和多模态的时空异常线索。

## 方法要点
- 同时处理视频与音频，并引入多视角输入，增强异常证据覆盖范围。
- 使用跨视角注意力与跨模态同步模块，缓解时序错位和融合效率问题。
- 整体框架建立在 Transformer 式统一建模之上，强调多源证据协同。

## 实验与局限
- 论文报告其在 UCF-Crime、ShanghaiTech 与 XD-Violence 上相对当时基线有明显优势。
- 代价是较高计算复杂度，说明多视角多模态路线在部署成本上仍有现实压力。

## 关联连接
- [[M2VAD]] — 论文提出的核心方法实体。
- [[WeaklySupervisedVideoAnomalyDetection]] — 该方法采用弱监督设定。
- [[MultimodalVideoAnomalyDetection]] — 该方法强调音视频联合建模。
