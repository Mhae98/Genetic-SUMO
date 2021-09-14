import os
import numpy as np
import tensorflow as tf
from stable_baselines3 import PPO
from sumo_rl import SumoEnvironment
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.monitor import Monitor
import random

import concurrent.futures as concurrent


def benchmark_static_time(env_name, time_0=5, time_1=5, time_2=5, time_3=5, episodes=10):
    print(f'Executing with times {time_0}, {time_1}, {time_2}, {time_3}')
    env = SumoEnvironment(net_file='nets/single/single.net.xml',
                          route_file=f'nets/single/{env_name}.rou.xml',
                          additional_file='nets/single/single.det.xml',
                          out_csv_name='out/a2c',
                          single_agent=True,
                          use_gui=False,
                          num_seconds=5000,
                          min_green=5,
                          max_depart_delay=5000)
    durations = [time_0, time_1, time_2, time_3]
    log_dir = os.path.join('Benchmark', f'Baseline_{env_name}_{time_0}-{time_1}-{time_2}-{time_3}')
    writer = tf.compat.v1.summary.FileWriter(log_dir)
    episode = 0
    steps = 0
    done = False
    env.reset()
    rewards = []
    action = 0
    episode_rewards = np.zeros(episodes)
    while episode < episodes:
        observation, reward, done, _ = env.step(action)
        rewards.append(reward)
        steps += 1

        current_phase = np.argmax(observation[-5:-1])
        phase_duration = observation[-1]
        if durations[current_phase] <= phase_duration:
            action = (action + 1) % 4

        if done:
            episode_rewards[episode] = sum(rewards)
            done = False
            env.reset()
            summary = tf.compat.v1.Summary()
            summary.value.add(tag='rewards/Episode_reward', simple_value=episode_rewards[episode])
            summary.value.add(tag='Episode length', simple_value=steps)
            print(f'Episode: {episode}\tReward: {episode_rewards[episode]}')
            writer.add_summary(summary, global_step=episode)
            writer.flush()
            rewards = []
            steps = 0
            episode += 1
    summary = tf.compat.v1.Summary()
    summary.value.add(tag='rewards/Average_reward', simple_value=sum(episode_rewards)/episode)
    writer.add_summary(summary, global_step=0)
    writer.close()
    env.close()


def benchmark_model(env_name, model_name, episodes=10):
    model = PPO.load(f'models/model_{model_name}')
    sumo_env = SumoEnvironment(net_file='nets/single/single.net.xml',
                               route_file=f'nets/single/{env_name}.rou.xml',
                               additional_file='nets/single/single.det.xml',
                               out_csv_name='out/a2c',
                               single_agent=True,
                               use_gui=False,
                               num_seconds=5000,
                               min_green=5,
                               max_depart_delay=5000)
    env = Monitor(sumo_env)
    env = DummyVecEnv([lambda: env])
    env = VecNormalize(env, norm_obs=True, norm_reward=False)
    log_dir = os.path.join('Benchmark', f'model_{model_name}')
    writer = tf.compat.v1.summary.FileWriter(log_dir)
    episode = 0
    steps = 0
    done = False
    observation = env.reset()
    rewards = []
    episode_rewards = np.zeros(episodes)
    while episode < episodes:
        action, _states = model.predict(observation)
        observation, reward, done, _ = env.step(action)
        rewards.append(reward[0])
        steps += 1

        if done:
            episode_rewards[episode] = sum(rewards)
            done = False
            env.reset()
            summary = tf.compat.v1.Summary()
            summary.value.add(tag='rewards/Episode_reward', simple_value=episode_rewards[episode])
            summary.value.add(tag='Episode length', simple_value=steps)
            print(f'Episode: {episode}\tReward: {episode_rewards[episode]}')
            writer.add_summary(summary, global_step=episode)
            writer.flush()
            rewards = []
            steps = 0
            episode += 1
    summary = tf.compat.v1.Summary()
    summary.value.add(tag='rewards/Average_reward', simple_value=sum(episode_rewards)/episode)
    writer.add_summary(summary, global_step=0)
    writer.close()
    env.close()


def benchmark_random(env_name, episodes=10):
    env = SumoEnvironment(net_file='nets/single/single.net.xml',
                          route_file=f'nets/single/{env_name}.rou.xml',
                          additional_file='nets/single/single.det.xml',
                          out_csv_name='out/a2c',
                          single_agent=True,
                          use_gui=False,
                          num_seconds=5000,
                          min_green=5,
                          max_depart_delay=5000)
    log_dir = os.path.join('Benchmark', 'Baseline_random')
    writer = tf.compat.v1.summary.FileWriter(log_dir)
    steps = 0
    done = False
    env.reset()
    rewards = []
    summary = tf.compat.v1.Summary()
    episode = 0
    episode_rewards = np.zeros(episodes)
    while episode < episodes:
        action = np.random.randint(0, 4)
        _, reward, done, _ = env.step(action)
        rewards.append(reward)
        steps += 1

        if done:
            episode_rewards[episode] = sum(rewards)
            done = False
            env.reset()
            summary = tf.compat.v1.Summary()
            summary.value.add(tag='rewards/Episode_reward', simple_value=episode_rewards[episode])
            summary.value.add(tag='Episode length', simple_value=steps)
            print(f'Episode: {episode}\tReward: {episode_rewards[episode]}')
            writer.add_summary(summary, global_step=episode)
            writer.flush()
            rewards = []
            steps = 0
            episode += 1
    summary = tf.compat.v1.Summary()
    summary.value.add(tag='rewards/Average_reward', simple_value=sum(episode_rewards)/episode)
    writer.add_summary(summary, global_step=0)
    writer.close()
    env.close()


def find_best_action(observation):
    # mapped action(bzw phase):relevant obs_index
    # phase_mapping = {0: [8, 9, 4, 5], 1: [6, 7, 10, 11], 2: [12, 13, 0, 1], 3: [2, 3, 14, 15]}
    standing_mapping = {0: [5, 9], 1: [7, 11], 2: [1, 13], 3: [3, 15]}
    time_mapping = {0: [4, 8], 1: [6, 10], 2: [0, 12], 3: [2, 14]}
    min_map = dict()
    for action in range(4):
        # chooses phase if cars are standing on corresponding detector
        if max([observation[index] for index in standing_mapping[action]]) == 1:
            return action
        # finds the shortest time since activation for each action
        min_map[action] = min([observation[index] for index in time_mapping[action]])
    vals = list(min_map.values())
    # choose the phase with the shortest time since activation
    chosen = vals.index(min(vals))
    # If Observations 0: Some cars may be waiting. Phase is chosen by random to ensure that all cars eventually pass
    if min(vals) == 0:
        chosen = random.randint(0, 3)
    return chosen


def benchmark_own_policy(name, episodes=10):
    env = SumoEnvironment(net_file='nets/single/single.net.xml',
                          route_file=f'nets/single/{name}.rou.xml',
                          additional_file='nets/single/single.det.xml',
                          out_csv_name='out/a2c',
                          single_agent=True,
                          use_gui=False,
                          num_seconds=5000,
                          min_green=5,
                          max_depart_delay=5000)
    log_dir = os.path.join('Benchmark', 'own_policy')
    writer = tf.compat.v1.summary.FileWriter(log_dir)
    episode = 0
    steps = 0
    rewards = []
    episode_rewards = np.zeros(episodes)
    done = False
    observation = env.reset()
    while episode < episodes:
        observation, reward, done, _ = env.step(find_best_action(observation))
        rewards.append(reward)
        steps += 1

        if done:
            episode_rewards[episode] = sum(rewards)
            done = False
            env.reset()
            summary = tf.compat.v1.Summary()
            summary.value.add(tag='rewards/Episode_reward', simple_value=episode_rewards[episode])
            summary.value.add(tag='Episode length', simple_value=steps)
            print(f'Episode: {episode}\tReward: {episode_rewards[episode]}')
            writer.add_summary(summary, global_step=episode)
            writer.flush()
            rewards = []
            steps = 0
            episode += 1
    summary = tf.compat.v1.Summary()
    summary.value.add(tag='rewards/Average_reward', simple_value=sum(episode_rewards)/episode)
    writer.add_summary(summary, global_step=0)
    writer.close()
    env.close()


if __name__ == '__main__':
    name = "day_time"
    benchmark_random(name, 1000)
    # episodes = 1000
    # benchmark_times = [(5, 5, 5, 5), (10, 10, 10, 10), (15, 15, 15, 15), (20, 20, 20, 20), (25, 25, 25, 25),
    #                    (30, 30, 30, 30), (10, 10, 10, 5), (20, 20, 20, 10)]
    # executor = concurrent.ProcessPoolExecutor(len(benchmark_times) + 3)
    # futures = [executor.submit(benchmark_static_time, name, t0, t1, t2, t3, episodes) for (t0, t1, t2, t3) in benchmark_times]
    # futures.append(executor.submit(benchmark_model, name, name, episodes))
    # futures.append(executor.submit(benchmark_own_policy, name, episodes))
    # futures.append(executor.submit(benchmark_random, name, episodes))
    # concurrent.wait(futures)
