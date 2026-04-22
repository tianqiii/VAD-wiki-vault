---
title: "摘要-vadmamba-exploring-state-space-models-for-fast-video-anomaly-detection"
type: source
tags: [来源, 论文, 视频异常检测]
sources: ["raw/09-archive/Lyu et al. - 2025 - VADMamba Exploring State Space Models for Fast Video Anomaly Detection.pdf"]
last_updated: 2026-04-22
---

## Metadata
- **作者**: Jiahao Lyu，Minghua Zhao，Jing Hu，Xuewen Huang，Yifei Chen，Shuangli Du
- **年份**: 2025
- **期刊/会议**: IEEE ICME 2025（2025 IEEE International Conference on Multimedia and Expo）
- **DOI / arXiv**: DOI: 10.1109/ICME59968.2025.11209020；arXiv: 未在公开信息中找到

## 核心摘要
这篇论文探索把 Mamba 状态空间模型用于视频异常检测，并提出 VADMamba。方法使用 VQ-MaU 作为核心结构，通过未来帧预测和光流重建双任务进行混合检测，再用 clip-level fusion evaluation 选择片段级更可靠的分数来源。作者特别关注推理效率，认为 CNN/Transformer 路线虽然精度高，但在长序列和实时部署上成本偏高。实验显示，VADMamba 在多个基准上兼顾了较快推理和较强检测表现，是状态空间模型进入 VAD 的一个清晰样板。

## 论文问题
- 如何把状态空间模型引入视频异常检测，以兼顾长序列建模与部署效率。
- 如何在预测式与重建式检测信号之间找到更稳的融合方式。

## 方法要点
- 以 VQ-MaU 为核心结构，把 Mamba 状态空间模型用于视频时序建模。
- 同时执行未来帧预测和光流重建两项任务，形成混合检测框架。
- 用 clip-level fusion evaluation 在片段级选择更可靠的异常分数来源。

## 实验与局限
- 论文的主要卖点是：在多个基准上同时获得较快推理与较强检测能力。
- 该路线仍属于无监督混合检测框架，效率优势明显，但最终效果仍取决于双任务融合是否稳定。

## 关联连接
- [[VADMamba]] — 论文提出的核心方法实体。
- [[StateSpaceModel]] — 该工作把状态空间模型引入 VAD。
- [[VideoAnomalyDetection]] — 属于无监督混合检测路线。
