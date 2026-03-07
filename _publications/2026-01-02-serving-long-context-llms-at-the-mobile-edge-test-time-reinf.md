---
title: "[ToN] Serving long-context LLMs at the mobile edge: Test-time reinforcement learning-based model caching and inference offloading"
collection: publications
category: manuscripts
permalink: /publication/serving-long-context-llms-at-the-mobile-edge-test-time-reinf
date: 2026-01-02
venue: 'IEEE Transactions on Networking'
citation: 'Minrui Xu, Dusit Niyato, and Christopher G Brinton. (2026). &quot;Serving long-context LLMs at the mobile edge: Test-time reinforcement learning-based model caching and inference offloading&quot; <i>IEEE Transactions on Networking</i>.'
paperurl: https://ieeexplore.ieee.org/document/11417298/
arxiv_id: "2501.14205"
abstract_source_label: "arXiv"
abstract_source_url: "https://arxiv.org/abs/2501.14205"
abstract_text: |-
  Large Language Models (LLMs) can perform zero-shot learning on unseen tasks and few-shot
  learning on complex reasoning tasks. However, resource-limited mobile edge networks struggle
  to support long-context LLM serving for LLM agents during multi-round interactions with
  users. Unlike stateless computation offloading and static service offloading in edge
  computing, optimizing LLM serving at edge servers is challenging because LLMs continuously
  learn from context which raises accuracy, latency, and resource consumption dynamics. In
  this paper, we propose a joint model caching and inference offloading framework that
  utilizes test-time deep reinforcement learning (T2DRL) to optimize deployment and execution
  strategies for long-context LLM serving. In this framework, we analyze the performance
  convergence and design an optimization problem considering the utilization of context
  windows in LLMs. Furthermore, the T2DRL algorithm can learn in both the training phase and
  the testing phase to proactively manage cached models and service requests and adapt to
  context changes and usage patterns during execution. To further enhance resource allocation
  efficiency, we propose a double Dutch auction (DDA) mechanism, which dynamically matches
  supply and demand while maximizing social welfare. Finally, experimental results demonstrate
  that the T2DRL algorithm can reduce system costs by at least 30% compared to baselines while
  guaranteeing the performance of LLM agents in real-world perception and reasoning tasks.
featured_figure: "/images/publications/serving-long-context-llms-at-the-mobile-edge-test-time-reinf/featured.png"
featured_figure_caption: "Fig. 1: Serving LLMs to handle inputs and tackle complex tasks using CoT prompting in mobile edge networks."
featured_figure_source_url: "https://arxiv.org/abs/2501.14205"
---
