import os
import numpy as np
import tensorflow as tf
from sumo_rl import SumoEnvironment

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
    while episode < episodes:
        observation, reward, done, _ = env.step(action)
        rewards.append(reward)
        steps += 1

        current_phase = np.argmax(observation[-5:-1])
        phase_duration = observation[-1]
        if durations[current_phase] <= phase_duration:
            action = (action + 1) % 4

        if done:
            done = False
            episode += 1
            env.reset()
            summary = tf.compat.v1.Summary()
            summary.value.add(tag='rollout/ep_rew_mean', simple_value=sum(rewards))
            summary.value.add(tag='rollout/ep_len_mean', simple_value=steps)
            print(f'Episode: {episode}\tReward: {sum(rewards)}')
            writer.add_summary(summary, global_step=episode)
            writer.flush()
            rewards = []
            steps = 0
    writer.close()
    env.close()


def benchmark_random(env_name, timesteps=20000):
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
    step = 0
    done = False
    env.reset()
    rewards = []
    summary = tf.compat.v1.Summary()
    writer.add_summary(summary, global_step=step)
    while step < timesteps:
        action = np.random.randint(0, 3)
        _, reward, done, _ = env.step(action)
        rewards.append(reward)
        step += 1
        if done:
            done = False
            env.reset()
            print(f'Step: {step}\tReward: {sum(rewards)}')
            summary.value.add(tag='rollout/ep_rew_mean', simple_value=sum(rewards))
            writer.flush()
            rewards = []
    # writer.close()
    env.close()


if __name__ == '__main__':
    name = "day_time"
    benchmark_times = [(5, 5, 5, 5), (10, 10, 10, 10), (15, 15, 15, 15), (20, 20, 20, 20), (25, 25, 25, 25),
                       (30, 30, 30, 30)]
    executor = concurrent.ProcessPoolExecutor(len(benchmark_times))
    futures = [executor.submit(benchmark_static_time, name, t0, t1, t2, t3, 10) for (t0, t1, t2, t3) in benchmark_times]
    concurrent.wait(futures)
