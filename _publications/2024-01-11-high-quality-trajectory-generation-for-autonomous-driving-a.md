---
title: "[GlobeCom] High-Quality Trajectory Generation for Autonomous Driving: A Lightweight Federated Learning-Based Diffusion Model"
collection: publications
category: conferences
permalink: /publication/high-quality-trajectory-generation-for-autonomous-driving-a
date: 2024-01-11
venue: 'IEEE Global Communications Conference'
citation: 'Runze Gao, Jiawen Kang, Bingkun Lai, Minrui Xu, Geng Sun, Tao Zhang, Weiting Zhang, and Dusit Yang. (2024). &quot;High-Quality Trajectory Generation for Autonomous Driving: A Lightweight Federated Learning-Based Diffusion Model&quot; <i>IEEE Global Communications Conference</i>.'
paperurl: https://ieeexplore.ieee.org/document/10901719/
abstract_source_label: "IEEE"
abstract_source_url: "https://ieeexplore.ieee.org/document/10901719/"
abstract_text: |-
  Vehicle trajectory data plays a pivotal role in simulation testing for autonomous driving.
  Hence, there exist well-established trajectory generation methods employing deep generative
  models to generate trajectories mapping the distribution of the original dataset, thereby
  augmenting existing trajectory datasets. However, these methods typically rely on large
  datasets gathered by governmental or organizational entities for central training, which may
  pose data privacy, security, and accessibility issues. Therefore, it is challenging to
  generate high-quality traffic trajectory data while preserving privacy which involves a
  delicate balance between these two objectives. To deal with this challenge, we introduce
  Federated Learning into the diffusion model and propose a Federated Learning-based diffusion
  model (FedDifftraj) to generate traffic trajectory data. Unlike existing central training
  methods, FedDifftraj aggregates model parameters uploaded by different vehicles and then
  updates a global model. Additionally, there is a substantial communication overhead incurred
  during the training of the federated diffusion model. Therefore, we quantize the local
  diffusion model before uploading it to the parameter server. Through extensive simulations
  on real-world datasets, FedDifftraj can generate high-quality traffic trajectory data that
  is consistent with the results of the central training while preserving privacy and reducing
  communication overhead by 93.74% when utilizing 8-bit quantization.
---
