---
title: "摘要-ds-ib-net-ultra-lightweight-weakly-supervised-video-anomaly-detection-through-synergistic-dual-streams-and-information-bottleneck"
type: source
tags: [来源, 论文, 视频异常检测]
sources: ["raw/09-archive/Zhu et al. - 2025 - DS-IB Net Ultra-Lightweight Weakly-Supervised Video Anomaly Detection through Synergistic Dual Stre.pdf"]
last_updated: 2026-04-22
---

## Metadata
- **作者**: Tao Zhu，Qi Yu，Heran Song，Yuheng Cheng，Shiyu Li，Yue Liu，Xinyi Tu，Kaiwen Luo
- **年份**: 2025
- **期刊/会议**: ACM Multimedia in Asia 2025（Proceedings of the 7th ACM International Conference on Multimedia in Asia）
- **DOI / arXiv**: DOI: 10.1145/3743093.3771006；arXiv: 未在公开信息中找到

## 核心摘要
这篇论文提出 DSIB-Net，一个面向弱监督视频异常检测的超轻量双流信息瓶颈框架。作者认为，现有方法在提升检测性能时往往付出了很高的计算代价，因此尝试用 Information Bottleneck 压缩正常动态中的冗余信息，同时再单独建立一条瞬时外观补偿支路来弥补被压缩掉的细节。随后，Adaptive Feature Arbitration 根据当前帧的外观证据动态调节动态表示的权重，使模型在“稳健建模正常动态”和“敏感捕捉瞬时异常外观”之间取得平衡。实验显示，DSIB-Net 在保持很低开销的前提下仍有很强的弱监督检测能力。

## 论文问题
- 如何在弱监督视频异常检测中降低计算开销，同时保持对异常证据的敏感性。
- 如何在压缩动态冗余信息与保留瞬时异常外观之间取得平衡。

## 方法要点
- 用 Information Bottleneck 压缩正常动态中的冗余信息，建立轻量主干。
- 增加瞬时外观补偿支路，专门保留容易被压缩掉的异常细节。
- 通过 Adaptive Feature Arbitration 根据外观证据动态调节动态表示的权重。

## 实验与局限
- 文中强调 DSIB-Net 在保持极低开销的同时仍具备很强的弱监督检测能力。
- 这条路线更偏工程效率优化，若异常主要依赖长时依赖而非瞬时外观，双流仲裁的收益可能受场景限制。

## 关联连接
- [[DSIBNet]] — 论文提出的核心方法实体。
- [[InformationBottleneck]] — 其方法核心来自信息瓶颈思想。
- [[WeaklySupervisedVideoAnomalyDetection]] — 属于轻量弱监督路线。
