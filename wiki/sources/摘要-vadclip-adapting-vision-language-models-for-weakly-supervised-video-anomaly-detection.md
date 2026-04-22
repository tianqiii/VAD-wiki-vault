---
title: "摘要-vadclip-adapting-vision-language-models-for-weakly-supervised-video-anomaly-detection"
type: source
tags: [来源, 论文, 视频异常检测, 弱监督, 视觉语言]
sources: ["raw/09-archive/Wu et al. - 2024 - VadCLIP Adapting Vision-Language Models for Weakly Supervised Video Anomaly Detection.pdf"]
last_updated: 2026-04-22
---

## Metadata
- **作者**: Peng Wu；Xuerong Zhou；Guansong Pang；Lingru Zhou；Qingsen Yan；Peng Wang；Yanning Zhang
- **年份**: 2024
- **期刊/会议**: AAAI 2024（The Thirty-Eighth AAAI Conference on Artificial Intelligence）
- **DOI / arXiv**: 未在 PDF 首页明确标注
- **代码**: https://github.com/nwpu-zxr/VadCLIP

## 核心摘要
这篇论文提出 VadCLIP，将冻结的 CLIP 直接迁移到弱监督视频异常检测（WSVAD）。与仅用视觉特征做 MIL 二分类的常见范式不同，VadCLIP 采用**双分支**：C-branch 做粗粒度二分类得到帧级异常置信；A-branch 将异常类别文本编码为向量，并与帧级视觉特征做语言-视觉对齐得到对齐图，从而支持细粒度的异常类别定位。为适配视频时序，论文提出轻量的 LGT-Adapter（局部窗口 Transformer + 全局 GCN）建模短/长时依赖；同时引入 learnable prompt 与 anomaly-focus visual prompt，把视频上下文注入文本侧表示；在弱监督条件下用 MIL-Align 近似对齐学习。论文在 XD-Violence 与 UCF-Crime 上报告了显著的提升。

## 论文问题
- 如何在仅有视频级标签的弱监督设置下，稳定地产生帧级异常分数并支持细粒度类别？
- 如何在不微调 CLIP 主干的前提下，将视觉-语言对齐能力迁移到视频时序任务？

## 方法要点
- **LGT-Adapter**：局部窗口自注意力捕捉邻域依赖 + GCN 捕捉全局关系。
- **双分支**：C-branch（分类）提供粗粒度异常注意；A-branch（对齐）提供细粒度类别对齐图。
- **Prompt 机制**：learnable prompt 与 anomaly-focus visual prompt 强化文本侧类别表示。
- **MIL-Align**：在弱监督下用 Top-K 聚合近似对齐训练。

## 实验与局限
- 论文主要评估在 XD-Violence / UCF-Crime 这类大规模弱监督数据集，指标与传统无监督 VAD 基准不同。
- 依赖预定义的异常类别文本标签与 prompt 设计；当异常类别集合变化时，需要重新组织文本侧表示。

## 关联连接
- [[VadCLIP]] — 论文提出的方法实体。
- [[WeaklySupervisedVideoAnomalyDetection]] — 上位任务设定。
- [[MultimodalVideoAnomalyDetection]] — 通过语言对齐引入跨模态语义（与纯视觉弱监督路线互补）。
- [[VideoAnomalyDetection]] — 上位任务。
