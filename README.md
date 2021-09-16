# Genetic-SUMO
## Setup 
It's recommended to use a conda environment with python 3.7. 

Install SUMO Environment as explained [here.](https://sumo.dlr.de/docs/Installing/index.html) 
(Note: some of the tools below require the SUMO_HOME variable to be set, most of the installers should install them correctly, if not try [this]([here.](https://sumo.dlr.de/docs/Installing/index.html)))


Install Stable baselines with pip `pip install pip install stable-baselines3[extra]`or  via `pip install -r requirements.tx`

Install our local sumo-rl fork like: 

```
git clone https://github.com/DaniHi/sumo-rl
cd sumo-rl
pip install -e .
```

## Get Started

### Run project
Now you can start f. e. ppo training with

```
python main.py
```


### Netconfig
Use sumo-gui with our net config f. e.

```
sumo-gui nets/single/single.sumocfg 
```
This will start the sumo-gui with the single xml configurations.

### Adapt network in netedit
To manually configure the net run

```
netedit nets/single/single.net.xml 
```


### Download real-world examples
Run

```
python $SUMO_HOME/tools/osmWebWizard.py
```

and choose whatever you want to download