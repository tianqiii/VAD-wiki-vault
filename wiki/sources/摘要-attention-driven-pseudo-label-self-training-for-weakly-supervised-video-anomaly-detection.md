---
title: "摘要-attention-driven-pseudo-label-self-training-for-weakly-supervised-video-anomaly-detection"
type: source
tags: [来源, 论文, 视频异常检测]
sources: ["raw/09-archive/Yang et al. - 2026 - Attention-driven pseudo-label self-training for weakly supervised video anomaly detection.pdf"]
last_updated: 2026-04-22
---

## Metadata
- **作者**: Zhiwei Yang，Jing Liu，Guansong Pang，Peng Wu，Zhaoyang Wu
- **年份**: 2026
- **期刊/会议**: Pattern Recognition
- **DOI / arXiv**: DOI: 10.1016/j.patcog.2026.113349；arXiv: 未在公开信息中找到

## 核心摘要
这篇论文提出一个注意力驱动的双分支框架，把伪标签生成和自训练从“串行两阶段”改成“同步协同优化”。第一分支使用自注意力与交叉注意力把异常视频中的异常片段和正常片段分离出来，并借助视频级分类结果和均值-方差去噪策略生成更干净的片段伪标签；第二分支则用多尺度时间特征交互模块训练片段分类器。作者的核心判断是，两阶段方法容易把早期噪声伪标签不断放大，而同步更新可以在训练过程中逐步修正。实验结果说明，这种同步式伪标签自训练框架在多个弱监督基准上都优于先前两阶段或多阶段方案。

## 论文问题
- 两阶段伪标签自训练为什么容易在弱监督 VAD 中不断放大早期噪声。
- 如何让伪标签生成与片段分类训练形成更稳定的相互校正机制。

## 方法要点
- 建立注意力驱动的双分支框架，把伪标签生成和自训练改成同步协同优化。
- 第一分支用自注意力、交叉注意力与去噪策略生成更干净的片段级伪标签。
- 第二分支用多尺度时间特征交互模块训练片段分类器，并在训练中持续反向修正伪标签质量。

## 实验与局限
- 论文报告该同步式伪标签自训练框架在多个弱监督基准上优于先前两阶段或多阶段方案。
- 该方法的有效性依赖伪标签与分类器的协同稳定性，若其中一支严重偏移，另一支也可能被拖累。

## 关联连接
- [[ADPLGVAD]] — 论文对应的方法实体。
- [[PseudoLabelSelfTraining]] — 该工作围绕同步式伪标签自训练展开。
- [[WeaklySupervisedVideoAnomalyDetection]] — 方法面向弱监督视频异常检测。
