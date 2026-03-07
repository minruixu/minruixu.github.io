---
title: "[ACM MM] One-Shot-but-Not-Degraded Federated Learning"
collection: publications
category: conferences
permalink: /publication/one-shot-but-not-degraded-federated-learning
date: 2024-01-03
venue: 'ACM Multimedia'
citation: 'Hui Zeng, Minrui Xu, Tongqing Zhou, Xinyi Wu, Jiawen Kang, Zhiping Cai, and Dusit Niyato. (2024). &quot;One-Shot-but-Not-Degraded Federated Learning&quot; <i>ACM Multimedia</i>.'
paperurl: https://doi.org/10.1145/3664647.3680715
abstract_source_label: "OpenAlex"
abstract_source_url: "https://openalex.org/W4403791634"
abstract_text: |-
  Transforming the multi-round vanilla Federated Learning (FL) into one-shot FL (OFL)
  significantly reduces the communication burden and makes a big leap toward practical
  deployment. However, we note that existing OFL methods all build on model lossy
  reconstruction (i.e., aggregating while partially discarding local knowledge in clients'
  models), which attains one-shot at the cost of degraded inference performance. By
  identifying the root cause of stressing too much on finding a one-fit-all model, this work
  proposes a novel one-shot FL framework by embodying each local model as an independent
  expert and leveraging a Mixture-of-Experts network to maintain all local knowledge intact. A
  dedicated self-supervised training process is designed to tune the network, where the sample
  generation is guided by approximating underlying distributions of local data and making
  distinct predictions among experts. Notably, the framework also fuels FL with flexible,
  data-free aggregation and heterogeneity tolerance. Experiments on 4 datasets show that the
  proposed framework maintains the one-shot efficiency, facilitates superior performance
  compared with 8 OFL baselines (+5.54% on CIFAR-10), and even attains over ×4 performance
  gain compared with 3 multi-round FL methods, while only requiring less than 85% trainable
  parameters. Our code will be available at https://github.com/zenghui9977/IntactOFL.
---
