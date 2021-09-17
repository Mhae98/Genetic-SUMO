# Genetic-SUMO
## Setup 
It's recommended to use a conda environment with python 3.7. 

### Install SUMO

#### Linux
Install SUMO latest version:

```
sudo add-apt-repository ppa:sumo/stable
sudo apt-get update
sudo apt-get install sumo sumo-tools sumo-doc 
```
Don't forget to set SUMO_HOME variable (default sumo installation path is /usr/share/sumo)
```
echo 'export SUMO_HOME="/usr/share/sumo"' >> ~/.bashrc
source ~/.bashrc
```

#### Windows

Install SUMO Environment as explained [here.](https://sumo.dlr.de/docs/Installing/index.html) 
(Note: some of the tools below require the SUMO_HOME variable to be set, most of the installers should install them correctly, if not try this [here.](https://sumo.dlr.de/docs/Installing/index.html))

## Install Stable-Baselines

Install Stable baselines with pip `pip install stable-baselines3[extra]`or  via `pip install -r requirements.txt`


## Install SUMO-RL
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


### Error Handling

If "error: command 'x86-64-linux-gnu-gcc' failed with exit status 1" try to 
install `sudo apt-get install python3-dev`
