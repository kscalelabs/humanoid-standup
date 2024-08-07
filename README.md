<p align="center">
  <picture>
    <img alt="K-Scale Open Source Robotics" src="https://media.kscale.dev/kscale-open-source-header.png" style="max-width: 100%;">
  </picture>
</p>

<div align="center">

[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/kscalelabs/ksim/blob/main/LICENSE)
[![Discord](https://img.shields.io/discord/1224056091017478166)](https://discord.gg/k5mSvCkYQh)
[![Wiki](https://img.shields.io/badge/wiki-humanoids-black)](https://humanoids.wiki)
<br />
[![python](https://img.shields.io/badge/-Python_3.11-blue?logo=python&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![black](https://img.shields.io/badge/Code%20Style-Black-black.svg?labelColor=gray)](https://black.readthedocs.io/en/stable/)
[![ruff](https://img.shields.io/badge/Linter-Ruff-red.svg?labelColor=gray)](https://github.com/charliermarsh/ruff)
<br />
[![Python Checks](https://github.com/kscalelabs/humanoid-standup/actions/workflows/test.yml/badge.svg)](https://github.com/kscalelabs/humanoid-standup/actions/workflows/test.yml)

</div>

# Humanoid Standup

Minimal training and inference code for making a humanoid robot stand up.

## Getting started
- `export DISPLAY=:0` if in a headless environmnet
- Run `train.py`!

## TODO

- [ ] Implement simple MJX environment using [Unitree G1 simulation artifacts](https://humanoids.wiki/w/Robot_Descriptions_List), similar to [this](https://gymnasium.farama.org/environments/mujoco/humanoid_standup)
- [ ] Implement simple PPO policy to try to make the robot stand up
- [ ] Parallelize using JAX

# Findings
- Low standard deviation for "overfitting test" does not work very well for PPO because need to converge upon actual solution. Cannot get to actual solution if do not explore a little. With that in mind, I think the model is generally getting too comfortable tricking the reward system by just losing as fast as posisble so doesn't have to deal with penalty
- Theory that model just trying to lose (to retain `is_healthy` while not losing as much height. It wants to fall as quick as possible so can reset) can be tested by adding "wait" and removing the mask. This effectively reduces the fact that reset will work. While the model is stuck in the failed state, it still is unhealthy and therefore loses out on reward.

# Currently tests:
- Hidden layer size of 256 shows progress (loss is based on state.q[2])

## Goals

- The goal for this repository is to provide a super minimal implementation of a PPO policy for making a humanoid robot stand up, with only three files:
  - `environment.py` defines a class for interacting with the environment
  - `train.py` defines the core training loop
  - `infer.py` generates a video clip of a trained model controlling a robot
