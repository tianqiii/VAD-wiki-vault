---
title: "摘要-eventvad-training-free-event-aware-video-anomaly-detection"
type: source
tags: [来源, 论文, 视频异常检测]
sources: ["raw/09-archive/Shao et al. - 2025 - EventVAD training-free event-aware video anomaly detection.pdf"]
last_updated: 2026-04-22
---

## Metadata
- **作者**: Yihua Shao，Haojin He，Sijie Li，Siyu Chen，Xinwei Long，Fanhu Zeng，Yuxuan Fan，Muyang Zhang，Ziyang Yan，Ao Ma，Xiaochen Wang，Hao Tang，Yan Wang，Shuyan Li
- **年份**: 2025
- **期刊/会议**: ACM Multimedia 2025（Proceedings of the 33rd ACM International Conference on Multimedia）
- **DOI / arXiv**: DOI: 10.1145/3746027.3754500；arXiv: 未在公开信息中找到

## 核心摘要
这篇论文提出 EventVAD，一种训练自由的视频异常检测框架。它的核心思想不是直接逐帧喂给多模态大模型，而是先通过 CLIP 特征、RAFT 光流、动态图和图注意力对长视频进行事件边界检测，把视频切分成语义一致的事件单元，再让 MLLM 进行层级化推理和评分。作者指出训练自由方法的主要痛点是单帧级大模型缺乏稳定时序建模能力，因此异常分数容易在长视频里抖动或错位。实验表明，这种“事件切分后再推理”的思路在 UCF-Crime 和 XD-Violence 上明显优于同类训练自由基线。

## 论文问题
- 如何在训练自由设定下，让大模型真正利用长视频中的时序结构，而不是停留在逐帧推理。
- 如何减少异常分数在长视频中的抖动、错位和局部误判。

## 方法要点
- 用 CLIP 特征、RAFT 光流、动态图和图注意力先做事件边界检测，把长视频切分成语义一致的事件单元。
- 再让 MLLM 对事件级单元做层级化推理与评分，而不是直接逐帧处理整段视频。
- 核心理念是“先把时间结构整理好，再调用大模型”，从而提升训练自由检测的稳定性。

## 实验与局限
- 文中报告其在 UCF-Crime 与 XD-Violence 上明显优于同类训练自由基线。
- 该路线依赖事件切分质量；若前置事件边界检测不稳，后续大模型推理的收益会被削弱。

## 关联连接
- [[EventVAD]] — 论文提出的核心方法实体。
- [[TrainingFreeVideoAnomalyDetection]] — 属于训练自由路线。
- [[MultimodalVideoAnomalyDetection]] — 同时利用视觉、光流和 MLLM。
