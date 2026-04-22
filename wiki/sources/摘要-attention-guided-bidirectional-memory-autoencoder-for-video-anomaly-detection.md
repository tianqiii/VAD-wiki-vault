---
title: "摘要-attention-guided-bidirectional-memory-autoencoder-for-video-anomaly-detection"
type: source
tags: [来源, 论文, 视频异常检测, 记忆增强, 双向]
sources: ["raw/09-archive/Le和Nguyen - 2026 - Attention-guided bidirectional memory autoencoder for video anomaly detection.pdf"]
last_updated: 2026-04-22
---

## Metadata
- **作者**: Anh Le；Quang Uy Nguyen
- **年份**: 2026
- **期刊/会议**: Neurocomputing（Vol. 670, 132589）
- **DOI / arXiv**: DOI: 10.1016/j.neucom.2025.132589
- **链接**: https://doi.org/10.1016/j.neucom.2025.132589

## 核心摘要
这篇论文提出 ABMA（Attention-guided Bidirectional Memory Autoencoder），把**双向记忆模块**与**空间注意力**嵌入自编码器，用“过去/未来双向上下文”共同重建目标帧，从而放大异常导致的时序不一致。与传统仅靠重建/预测误差的无监督范式不同，ABMA 还用 skip-frame 合成伪异常，在训练时同时使用正常与伪异常样本，通过“正常损失 + 反向的异常损失”抑制模型对伪异常的重建能力。推理时，论文将**图像域误差**与**潜空间到记忆项的距离**融合，并取 past/future 两方向的最大值来得到帧级异常分数。实验覆盖 Ped2、Avenue、ShanghaiTech、IITB-Corridor，并展示对短时/细微异常更稳健。

## 论文问题
- 记忆增强的自编码器仍可能对细微异常不敏感：如何同时利用过去/未来上下文提升可分性？
- 在缺少异常标注的前提下：如何用“可控伪异常”训练出更强的异常辨别能力？

## 方法要点
- **ABM（Attention-guided Bidirectional Memory）**：过去/未来两个记忆子空间，读取时对记忆项加权汇聚，更新时仅用正常特征。
- **空间注意力（SA）**：在融合后的特征上做 avg/max pooling 形成注意力图，突出关键区域。
- **伪异常训练**：用 skip-frame 合成伪异常，异常损失项显式“拉大”伪异常的预测/重建误差。
- **异常分数**：图像域 PSNR/误差 + 特征到最近记忆项距离，融合并归一化。

## 实验与局限
- 论文报告在多基准与多场景（长异常、短异常、缺失/模糊、跨数据集）下整体领先。
- 伪异常的构造方式与注入概率会影响效果；论文本身也讨论了在遮挡/静止/远距离异常上的失败案例。

## 关联连接
- [[ABMA]] — 论文提出的方法实体。
- [[MemoryAugmentedVideoAnomalyDetection]] — 记忆增强路线的代表之一。
- [[VideoAnomalyDetection]] — 上位任务。
- [[BiSP]] — 论文相关工作中覆盖的双向预测式路线代表之一（用户指出该论文引用 BiSP）。
