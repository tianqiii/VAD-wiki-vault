---
title: "VadCLIP"
type: entity
tags: [方法, 视频异常检测, 弱监督, 视觉语言]
sources: ["raw/09-archive/Wu et al. - 2024 - VadCLIP Adapting Vision-Language Models for Weakly Supervised Video Anomaly Detection.pdf"]
last_updated: 2026-04-22
---

## 定义
VadCLIP 是一种利用冻结 CLIP 的视觉-语言对齐能力来做弱监督视频异常检测的方法，通过“双分支（分类 + 对齐）+ 时序适配器 + prompt 机制”同时支持粗粒度与细粒度异常检测。

## 关键信息
- C-branch 产出帧级异常置信并为 A-branch 提供异常聚焦的视觉提示。
- A-branch 用文本类别向量与帧级视觉向量对齐，得到细粒度对齐图并用 MIL-Align 在弱监督下训练。
- LGT-Adapter 用局部窗口 Transformer + 全局 GCN 建模时序依赖。

## 关联连接
- [[摘要-vadclip-adapting-vision-language-models-for-weakly-supervised-video-anomaly-detection]] — 来源。
- [[WeaklySupervisedVideoAnomalyDetection]] — 上位任务设定。
- [[MultimodalVideoAnomalyDetection]] — 通过语言对齐引入跨模态语义。
- [[VideoAnomalyDetection]] — 上位任务。
