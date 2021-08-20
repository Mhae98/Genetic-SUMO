import os
import sys
import random

from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")
from sumo_rl import SumoEnvironment
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor


def find_best_action(observation):
    # mapped action(bzw phase):relevant obs_index
    # phase_mapping = {0: [8, 9, 4, 5], 1: [6, 7, 10, 11], 2: [12, 13, 0, 1], 3: [2, 3, 14, 15]}
    standing_mapping = {0: [5, 9], 1: [7, 11], 2: [1, 13], 3: [3, 15]}
    time_mapping = {0: [4, 8], 1: [6, 10], 2: [0, 12], 3: [2, 14]}
    min_map = dict()
    for action in range(4):
        # chooses phase if cars are standing on it
        if max([observation[index] for index in standing_mapping[action]]) == 1:
            return action
        # finds to each action the shortest time since activation
        min_map[action] = min([observation[index] for index in time_mapping[action]])
    vals = list(min_map.values())
    # choose the phase with the shortest time since activation
    return vals.index(min(vals))


def simple_environment():
    env = SumoEnvironment(net_file='nets/single/single.net.xml',
                          route_file='nets/single/randomTrips.rou.xml',
                          additional_file='nets/single/single.det.xml',
                          out_csv_name='a2c',
                          single_agent=True,
                          use_gui=True,
                          num_seconds=100000,
                          min_green=5,
                          max_depart_delay=0)
    observation = env.reset()
    done = False

    while not done:
        observation, reward, done, _ = env.step(find_best_action(observation))


if __name__ == '__main__':
    env = SumoEnvironment(net_file='nets/single/single.net.xml',
                          route_file='nets/single/randomTrips.rou.xml',
                          additional_file='nets/single/single.det.xml',
                          out_csv_name='a2c',
                          single_agent=True,
                          use_gui=False,
                          num_seconds=5000,
                          min_green=5,
                          max_depart_delay=0)
    env = Monitor(env)
    env = DummyVecEnv([lambda: env])
    env = VecNormalize(env, norm_obs=True) #, norm_reward=True)
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log="./ppo_tensorboard/")
    model.learn(total_timesteps=2000, tb_log_name="first_run")

    observation = env.reset()
    done = False

    while not done:
        action, _states = model.predict(observation)
        observation, reward, done, _ = env.step(action)
    env.close()
