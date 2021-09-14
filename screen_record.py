import time
import numpy as np
from stable_baselines3 import PPO
from sumo_rl import SumoEnvironment
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.monitor import Monitor
import random


def benchmark_model(env_name, model_name):
    model = PPO.load(f'models/model_{model_name}')
    sumo_env = SumoEnvironment(net_file='nets/single/single.net.xml',
                               route_file=f'nets/single/{env_name}.rou.xml',
                               additional_file='nets/single/single.det.xml',
                               out_csv_name='out/a2c',
                               single_agent=True,
                               use_gui=True,
                               num_seconds=5000,
                               min_green=5,
                               max_depart_delay=5000)
    env = Monitor(sumo_env)
    env = DummyVecEnv([lambda: env])
    env = VecNormalize(env, norm_obs=True, norm_reward=False)

    done = False
    observation = env.reset()
    rewards = []
    input('Press enter to start simulation ')
    time.sleep(2)
    while not done:
        action, _states = model.predict(observation)
        observation, reward, done, _ = env.step(action)
        rewards.append(reward[0])

    print(f'RL-model\t\t Reward: {sum(rewards)}')
    env.close()


def benchmark_static_time(env_name, time_0=5, time_1=5, time_2=5, time_3=5):
    print(f'Executing static phase times with times {time_0}, {time_1}, {time_2}, {time_3}')
    env = SumoEnvironment(net_file='nets/single/single.net.xml',
                          route_file=f'nets/single/{env_name}.rou.xml',
                          additional_file='nets/single/single.det.xml',
                          out_csv_name='out/a2c',
                          single_agent=True,
                          use_gui=True,
                          num_seconds=5000,
                          min_green=5,
                          max_depart_delay=5000)
    durations = [time_0, time_1, time_2, time_3]
    done = False
    env.reset()
    rewards = []
    action = 0
    input('Press enter to start simulation ')
    time.sleep(2)
    while not done:
        observation, reward, done, _ = env.step(action)
        rewards.append(reward)
        current_phase = np.argmax(observation[-5:-1])
        phase_duration = observation[-1]
        if durations[current_phase] <= phase_duration:
            action = (action + 1) % 4
    print(f'Static time {durations[0]}-{durations[1]}-{durations[2]}-{durations[3]}\t\tReward: {sum(rewards)}')
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


def benchmark_own_policy(name):
    env = SumoEnvironment(net_file='nets/single/single.net.xml',
                          route_file=f'nets/single/{name}.rou.xml',
                          additional_file='nets/single/single.det.xml',
                          out_csv_name='out/a2c',
                          single_agent=True,
                          use_gui=True,
                          num_seconds=5000,
                          min_green=5,
                          max_depart_delay=5000)
    rewards = []
    done = False
    observation = env.reset()
    input('Press enter to start simulation ')
    time.sleep(2)
    while not done:
        observation, reward, done, _ = env.step(find_best_action(observation))
        rewards.append(reward)

    print(f'Own policy\t\tReward: {sum(rewards)}')
    env.close()


if __name__ == '__main__':
    name = 'day_time'
    benchmark_model(name, name)
    benchmark_own_policy(name)
    benchmark_static_time(name, 30, 30, 30, 30)
    benchmark_static_time(name, 5, 5, 5, 5)
