---
title: "摘要-video-anomaly-detection-via-spatio-temporal-pseudo-anomaly-generation-a-unified-approach"
type: source
tags: [来源, 论文, 视频异常检测]
sources: ["raw/09-archive/Rai et al. - 2024 - Video Anomaly Detection via Spatio-Temporal Pseudo-Anomaly Generation  A Unified Approach.pdf"]
last_updated: 2026-04-22
---

## Metadata
- **作者**: Ayush K. Rai，Tarun Krishna，Feiyan Hu，Alexandru Drimbarean，Kevin McGuinness，Alan F. Smeaton，Noel E. O’Connor
- **年份**: 2024
- **期刊/会议**: CVPRW 2024（2024 IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops）
- **DOI / arXiv**: DOI: 10.1109/CVPRW63382.2024.00393；arXiv: 未在公开信息中找到

## 核心摘要
这篇论文提出一种统一的视频异常检测框架，核心是从正常视频中合成更通用的时空伪异常。作者指出，先前伪异常方法往往依赖强假设，比如固定补丁入侵或固定跳帧速度，这会让模型只对某些人为构造的异常敏感，而缺乏真实开放集异常的泛化能力。为此，论文用预训练 latent diffusion model 对图像被遮挡区域进行修补，生成空间伪异常；同时对正常光流进行 mixup 扰动，生成时间伪异常。检测时，再统一聚合重建质量、时间不规则性和语义不一致性三类指标，从而在多个基准上取得有竞争力的 OCC 检测表现，并强调这种伪异常具有一定跨数据集可迁移性。

## 论文问题
- 先前的伪异常生成方法为什么容易过拟合某一类人为构造异常，而缺乏对真实开放集异常的泛化能力。
- 如何从正常视频中生成更通用的时空近异常样本来收紧检测边界。

## 方法要点
- 用预训练 latent diffusion model 对图像被遮挡区域进行修补，生成空间伪异常。
- 对正常光流进行 mixup 扰动，生成时间伪异常。
- 检测阶段统一聚合重建质量、时间不规则性和语义不一致性三类指标，形成统一异常评分。

## 实验与局限
- 论文结论是：该统一伪异常生成框架在多个基准上取得了有竞争力的 OCC 表现，并具有一定跨数据集可迁移性。
- 这一路线仍建立在人工构造近异常的假设上，其泛化增益高度依赖伪异常是否足够贴近真实开放集异常边界。

## 关联连接
- [[PseudoAnomalyGenerationVAD]] — 论文对应的方法实体。
- [[PseudoAnomalyGeneration]] — 该工作讨论的核心技术概念。
- [[VideoAnomalyDetection]] — 方法面向无监督视频异常检测任务。
