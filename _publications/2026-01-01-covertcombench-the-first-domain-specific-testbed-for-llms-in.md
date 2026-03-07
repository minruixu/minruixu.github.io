---
title: "[Preprint] CovertComBench: The First Domain-Specific Testbed for LLMs in Wireless Covert Communication"
collection: publications
category: preprints
permalink: /publication/covertcombench-the-first-domain-specific-testbed-for-llms-in
date: 2026-01-01
venue: 'arXiv preprint arXiv:2601.18315'
citation: 'Zhaozhi Liu, Jianrui Chen, Yuanai Xie, Yuan Jiang, Minrui Xu, Xiao Zhang, Peng Lai, and Zhenyu Zhou. (2026). &quot;CovertComBench: The First Domain-Specific Testbed for LLMs in Wireless Covert Communication&quot; <i>arXiv preprint arXiv:2601.18315</i>.'
paperurl: https://arxiv.org/abs/2601.18315
arxiv_id: "2601.18315"
abstract_source_label: "arXiv"
abstract_source_url: "https://arxiv.org/abs/2601.18315"
abstract_text: |-
  The integration of Large Language Models (LLMs) into wireless networks presents significant
  potential for automating system design. However, unlike conventional throughput
  maximization, Covert Communication (CC) requires optimizing transmission utility under
  strict detection-theoretic constraints, such as Kullback-Leibler divergence limits. Existing
  benchmarks primarily focus on general reasoning or standard communication tasks and do not
  adequately evaluate the ability of LLMs to satisfy these rigorous security constraints. To
  address this limitation, we introduce CovertComBench, a unified benchmark designed to assess
  LLM capabilities across the CC pipeline, encompassing conceptual understanding (MCQs),
  optimization derivation (ODQs), and code generation (CGQs). Furthermore, we analyze the
  reliability of automated scoring within a detection-theoretic ``LLM-as-Judge'' framework.
  Extensive evaluations across state-of-the-art models reveal a significant performance
  discrepancy. While LLMs achieve high accuracy in conceptual identification (81%) and code
  implementation (83%), their performance in the higher-order mathematical derivations
  necessary for security guarantees ranges between 18% and 55%. This limitation indicates that
  current LLMs serve better as implementation assistants rather than autonomous solvers for
  security-constrained optimization. These findings suggest that future research should focus
  on external tool augmentation to build trustworthy wireless AI systems.
featured_figure: "/images/publications/covertcombench-the-first-domain-specific-testbed-for-llms-in/featured.png"
featured_figure_caption: |-
  Fig. 1: The construction pipeline of CovertComBench. The four main stages are: (1)
  Contamination Check, (2) Context Extraction, (3) Question Construction, and (4) Experts
  Review.
featured_figure_source_url: "https://arxiv.org/abs/2601.18315"
---
