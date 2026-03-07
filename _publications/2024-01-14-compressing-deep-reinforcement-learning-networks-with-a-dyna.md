---
title: "[TVT] Compressing deep reinforcement learning networks with a dynamic structured pruning method for autonomous driving"
collection: publications
category: manuscripts
permalink: /publication/compressing-deep-reinforcement-learning-networks-with-a-dyna
date: 2024-01-14
venue: 'IEEE Transactions on Vehicular Technology'
citation: 'Wensheng Su, Zhenni Li, Minrui Xu, Jiawen Kang, Dusit Niyato, and Shengli Xie. (2024). &quot;Compressing deep reinforcement learning networks with a dynamic structured pruning method for autonomous driving&quot; <i>IEEE Transactions on Vehicular Technology</i>.'
paperurl: https://ieeexplore.ieee.org/document/10529967/
abstract_source_label: "Institute of Electrical and Electronics Engineers (IEEE)"
abstract_source_url: "https://ieeexplore.ieee.org/document/10529967/"
abstract_text: |-
  Deepreinforcement learning (DRL) has shown remarkable success in complex autonomous driving
  scenarios. However, DRL models inevitably bring high memory consumption and computation,
  which hinders their wide deployment in resource-limited autonomous driving devices.
  Structured Pruning has been recognized as a useful method to compress and accelerate DRL
  models, but it is still challenging to estimate the contribution of a parameter (i.e.,
  neuron) to DRL models. In this paper, we introduce a novel dynamic structured pruning
  approach that gradually removes a DRL model's unimportant neurons during the training stage.
  Our method consists of two steps, i.e. training DRL models with a group sparse regularizer
  and removing unimportant neurons with a dynamic pruning threshold. To efficiently train the
  DRL model with a small number of important neurons, we employ a neuron-importance group
  sparse regularizer. In contrast to conventional regularizers, this regularizer imposes a
  penalty on redundant groups of neurons that do not significantly influence the output of the
  DRL model. Furthermore, we design a novel structured pruning strategy to dynamically
  determine the pruning threshold and gradually remove unimportant neurons with a binary mask.
  Therefore, our method can remove not only redundant groups of neurons of the DRL model but
  also achieve high and robust performance. Experimental results show that the proposed method
  is competitive with existing DRL pruning methods on discrete control environments (i.e.,
  CartPole-v1 and LunarLander-v2) and MuJoCo continuous environments (i.e., Hopper-v3 and
  Walker2D-v3). Specifically, our method effectively compresses 93% neurons and 96% weights of
  the DRL model in four challenging DRL environments with slight accuracy degradation.
---
