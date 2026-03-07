---
title: "[TSC] pfedcal: Lightweight personalized federated learning with adaptive calibration strategy"
collection: publications
category: manuscripts
permalink: /publication/pfedcal-lightweight-personalized-federated-learning-with-ada
date: 2025-01-07
venue: 'IEEE Transactions on Services Computing'
citation: 'Dongshang Deng, Xuangou Wu, Tao Zhang, Chaocan Xiang, Wei Zhao, Minrui Xu, Jiawen Kang, Zhu Han, and Dusit Niyato. (2025). &quot;pfedcal: Lightweight personalized federated learning with adaptive calibration strategy&quot; <i>IEEE Transactions on Services Computing</i>.'
paperurl: https://ieeexplore.ieee.org/document/10937074/
abstract_source_label: "Institute of Electrical and Electronics Engineers (IEEE)"
abstract_source_url: "https://ieeexplore.ieee.org/document/10937074/"
abstract_text: |-
  Federated learning (FL) is a promising artificial intelligence framework that enables
  clients to collectively train models with data privacy. However, in real-world scenarios, to
  construct practical FL frameworks, several challenges have to be addressed, including
  statistical heterogeneity, constrained resources, and fairness. Therefore, we first
  investigate an <italic xmlns:mml="http://www.w3.org/1998/Math/MathML"
  xmlns:xlink="http://www.w3.org/1999/xlink">aggregation gap</i> caused by statistical
  heterogeneity during local model initialization, which not only causes additional
  computational overhead for clients but also leads to the degradation of fairness. To bridge
  this gap, we propose <italic xmlns:mml="http://www.w3.org/1998/Math/MathML"
  xmlns:xlink="http://www.w3.org/1999/xlink">pFedCal</i>, a novel <underline
  xmlns:mml="http://www.w3.org/1998/Math/MathML"
  xmlns:xlink="http://www.w3.org/1999/xlink">p</u>ersonalized <underline
  xmlns:mml="http://www.w3.org/1998/Math/MathML"
  xmlns:xlink="http://www.w3.org/1999/xlink">fed</u>erated learning with lightweight adaptive
  <underline xmlns:mml="http://www.w3.org/1998/Math/MathML"
  xmlns:xlink="http://www.w3.org/1999/xlink">cal</u>ibration strategy that performs
  calibration compensation through the prior knowledge of clients. Specifically, we introduce
  compensation for each client at the model initialization, with the compensation derived from
  the global gradient and the latest gradient bias. To enhance the calibration effect, we
  introduce a smoothing-based calibration strategy, and we design an adaptive calibration
  strategy. A representative example demonstrates that the proposed calibration and smoothing
  strategies improve fairness for clients. The theoretical analysis indicates that with an
  appropriate learning rate, pFedCal converges to a first-order stationary point for non-
  convex loss functions. Comprehensive experimental results show that pFedCal achieves faster
  convergence, higher accuracy, and improved fairness than the state-of-the-art methods.
---
