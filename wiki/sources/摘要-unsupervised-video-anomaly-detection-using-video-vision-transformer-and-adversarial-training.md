---
title: "摘要-unsupervised-video-anomaly-detection-using-video-vision-transformer-and-adversarial-training"
type: source
tags: [来源, 论文, 视频异常检测]
sources: ["raw/09-archive/Kobayashi et al. - 2025 - Unsupervised video anomaly detection using video vision transformer and adversarial training.pdf"]
last_updated: 2026-04-22
---

## Metadata
- **作者**: Shimpei Kobayashi，Akiyoshi Hizukuri，Ryohei Nakayama
- **年份**: 2025
- **期刊/会议**: IEEE Access
- **DOI / arXiv**: DOI: 10.1109/ACCESS.2025.3554813；arXiv: 未在公开信息中找到

## 核心摘要
这篇论文提出一个结合 ViViT、未来帧预测、光流幅值预测和 U-Net 判别器的无监督视频异常检测框架。作者认为仅依赖未来帧预测会受到动态背景噪声干扰，因此把光流幅值和对抗训练一起引入，以同时增强运动建模与异常区域显著性。方法使用生成器同时预测未来帧和光流，再用判别器中层特征对差分图进行再加权，从而压制静态区域噪声。实验结果显示，这种“ViViT 编码 + 光流预测 + 对抗细化”的组合优于文中多组基线。

## 论文问题
- 仅用未来帧预测做无监督 VAD 时，如何减轻动态背景噪声和静态区域误差的干扰。
- 如何让异常区域在预测误差图中更显著，而不是被背景扰动淹没。

## 方法要点
- 用 ViViT 编码视频时序信息，再同时预测未来帧和光流幅值。
- 引入 U-Net 判别器，并利用其中层特征对差分图再加权，以压制静态区域噪声。
- 核心策略是把“预测式建模”和“对抗式显著性细化”组合起来。

## 实验与局限
- 文中结果显示该组合优于多组无监督对比基线。
- 该路线结构较复杂，涉及生成器、光流预测与判别器，多模块协同训练的稳定性仍是潜在成本。

## 关联连接
- [[ViViTAdversarialVAD]] — 论文对应的方法实体。
- [[VideoAnomalyDetection]] — 方法面向无监督视频异常检测。
- [[StateSpaceModel]] — 虽然本文未使用状态空间模型，但与后续高效时序路线形成对照。
