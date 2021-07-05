import os
import sys
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")
from sumo_rl import SumoEnvironment
from sumo_rl.util.gen_route import write_route_file


if __name__ == '__main__':
    env = SumoEnvironment(net_file='2x2.net.xml',
                          route_file='2x2.rou.xml',
                          out_csv_name='a2c',
                          single_agent=True,
                          use_gui=False,
                          num_seconds=100000,
                          min_green=5,
                          max_depart_delay=0)
    env.reset()
    print("Step1:")
    print(env.step(3.))

