---
title: "摘要-prodisc-vad-an-efficient-system-for-weakly-supervised-anomaly-detection-in-video-surveillance-applications"
type: source
tags: [来源, 论文, 视频异常检测]
sources: ["raw/09-archive/Zhu et al. - 2025 - ProDisc-VAD An Efficient System for Weakly-Supervised Anomaly Detection in Video Surveillance Appli.pdf"]
last_updated: 2026-04-22
---

## Metadata
- **作者**: Tao Zhu，Qi Yu，Xinru Dong，Shiyu Li，Yue Liu，Jinlong Jiang，Lei Shu
- **年份**: 2025
- **期刊/会议**: IEEE SMC 2025（2025 IEEE International Conference on Systems, Man, and Cybernetics）
- **DOI / arXiv**: DOI: 10.1109/SMC58881.2025.11343488；arXiv: 未在公开信息中找到

## 核心摘要
这篇论文提出 ProDisc-VAD，一个面向弱监督视频异常检测的高效轻量框架。方法把“正常性原型建模”和“极值伪实例对比学习”结合起来，用 Prototype Interaction Layer 建立受控正常基线，再用 PIDE 只挑最高分和最低分实例做对比约束，减少中间噪声伪标签带来的误导。作者强调，与其在大模型和重主干上继续堆成本，不如把监督信号提纯到最可靠的部分。实验表明，ProDisc-VAD 在保持极少参数量的同时，在 ShanghaiTech 与 UCF-Crime 上都达到了很有竞争力的性能。

## 论文问题
- 在弱监督 VAD 中，如何减少噪声伪标签对训练的持续误导。
- 如何在保持模型轻量的前提下，仍然获得有竞争力的检测性能。

## 方法要点
- 用 Prototype Interaction Layer 建立可控的正常性原型基线。
- 用 PIDE 只对最高分和最低分实例施加对比约束，把监督集中到最可靠的片段上。
- 核心思想是“提纯监督信号”，而不是继续堆叠更重的主干或大模型。

## 实验与局限
- 文中强调其在 ShanghaiTech 与 UCF-Crime 上以极少参数量取得了很有竞争力的性能。
- 该路线对极值实例选择策略较敏感，若异常分数排序本身偏移，提纯监督的收益可能受限。

## 关联连接
- [[ProDiscVAD]] — 论文提出的核心方法实体。
- [[WeaklySupervisedVideoAnomalyDetection]] — 方法面向弱监督设定。
- [[PseudoLabelSelfTraining]] — 通过极值伪标签增强判别学习。
