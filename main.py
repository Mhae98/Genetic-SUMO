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

    #wenn obs alle 0, aber noch warten, dann per random wählen, damit alle irgendwann wegkommen
    return vals.index(min(vals))

def action_static_daytime(observation):
    standing_mapping = {0: [5, 9], 1: [7, 11], 2: [1, 13], 3: [3, 15]}
    time_mapping = {0: [4, 8], 1: [6, 10], 2: [0, 12], 3: [2, 14]}

    return 0

def simple_environment():
    env = SumoEnvironment(net_file='nets/single/single.net.xml',
                          route_file='nets/single/random.rou.xml',
                          additional_file='nets/single/single.det.xml',
                          out_csv_name='a2c',
                          single_agent=True,
                          use_gui=False,
                          num_seconds=100000,
                          min_green=5,
                          max_depart_delay=10)
    observation = env.reset()
    done = False

    while not done:
        observation, reward, done, _ = env.step(find_best_action(observation))


def train_model(env, name, timesteps):
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log="./ppo_tensorboard/")
    model.learn(total_timesteps=timesteps, tb_log_name=name)
    model.save(f'models/model_{name}')
    return model


def predict_model(model, env):
    sumo_env.use_gui = True
    observation = env.reset()
    done = False
    input("Press enter to continue ")
    while not done:
        action, _states = model.predict(observation)
        observation, reward, done, _ = env.step(action)


def run_environment_with_ppo(env, name, timesteps=20000, train=True):
    if train:
        model = train_model(env, name, timesteps)
    else:
        model = PPO.load(f'models/model_{name}')
    predict_model(model, env)


if __name__ == '__main__':
    name = "day_time_high"
    sumo_env = SumoEnvironment(net_file='nets/single/single.net.xml',
                               route_file=f'nets/single/{name}.rou.xml',
                               additional_file='nets/single/single.det.xml',
                               out_csv_name='out/a2c',
                               single_agent=True,
                               use_gui=False,
                               num_seconds=4800,
                               min_green=5,
                               max_depart_delay=12)
    env = Monitor(sumo_env)
    env = DummyVecEnv([lambda: env])
    env = VecNormalize(env, norm_obs=True)

    run_environment_with_ppo(env, name, train=False, timesteps=2e6)

