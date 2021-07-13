import os
import sys
import random
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")
from sumo_rl import SumoEnvironment
from sumo_rl.util.gen_route import write_route_file

if __name__ == '__main__':
    env = SumoEnvironment(net_file='nets/single/single.net.xml',
                          route_file='nets/single/single.rou.xml',
                          out_csv_name='a2c',
                          single_agent=True,
                          use_gui=True,
                          num_seconds=100000,
                          min_green=5,
                          max_depart_delay=0)
    env.reset()

    ongoing = True
    while ongoing:
        user_in = input('Select action: ')
        if user_in == 'S':
            ongoing = False
            break
        try:
            action = float(user_in)
            if action > 3 or action < 0:
                raise ValueError
        except ValueError:
            action = random.randint(0, 3)
        print(f'Selected action: {action}')
        print(env.step(action)[0])

