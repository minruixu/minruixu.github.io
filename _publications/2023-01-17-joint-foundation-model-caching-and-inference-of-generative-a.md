---
title: "[GlobeCom] Joint foundation model caching and inference of generative ai services for edge intelligence"
collection: publications
category: conferences
permalink: /publication/joint-foundation-model-caching-and-inference-of-generative-a
date: 2023-01-17
venue: 'IEEE Global Communications Conference'
citation: 'Minrui Xu, Dusit Niyato, Hongliang Zhang, Jiawen Kang, Zehui Xiong, Shiwen Mao, and Zhu Han. (2023). &quot;Joint foundation model caching and inference of generative ai services for edge intelligence&quot; <i>IEEE Global Communications Conference</i>.'
paperurl: https://ieeexplore.ieee.org/document/10436771/
arxiv_id: "2305.12130"
abstract_source_label: "arXiv"
abstract_source_url: "https://arxiv.org/abs/2305.12130"
abstract_text: |-
  With the rapid development of artificial general intelligence (AGI), various multimedia
  services based on pretrained foundation models (PFMs) need to be effectively deployed. With
  edge servers that have cloud-level computing power, edge intelligence can extend the
  capabilities of AGI to mobile edge networks. However, compared with cloud data centers,
  resource-limited edge servers can only cache and execute a small number of PFMs, which
  typically consist of billions of parameters and require intensive computing power and GPU
  memory during inference. To address this challenge, in this paper, we propose a joint
  foundation model caching and inference framework that aims to balance the tradeoff among
  inference latency, accuracy, and resource consumption by managing cached PFMs and user
  requests efficiently during the provisioning of generative AI services. Specifically,
  considering the in-context learning ability of PFMs, a new metric named the Age of Context
  (AoC), is proposed to model the freshness and relevance between examples in past
  demonstrations and current service requests. Based on the AoC, we propose a least context
  caching algorithm to manage cached PFMs at edge servers with historical prompts and
  inference results. The numerical results demonstrate that the proposed algorithm can reduce
  system costs compared with existing baselines by effectively utilizing contextual
  information.
featured_figure: "/images/publications/joint-foundation-model-caching-and-inference-of-generative-a/featured.png"
featured_figure_caption: "Fig. 1: Joint foundation model caching and inference of generative AI services for edge intelligence."
featured_figure_source_url: "https://arxiv.org/abs/2305.12130"
---
