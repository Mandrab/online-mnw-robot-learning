# Online learning of Robot controlled by Nanowire Networks

This repository contains the code used for various experiments with robots and Nanowire Networks.

## Published works

The code of this repository has been used for the experimental part of the following works:

- [On the performance of online adaptation of robots controlled by nanowire networks - Article](https://ieeexplore.ieee.org/abstract/document/10366266)
- [Online Adaptation of Robots Controlled by Nanowire Networks: A Preliminary Study - Article](https://link.springer.com/chapter/10.1007/978-3-031-31183-3_14)
- [Online adaptation of robots controlled by nanowire networks - Master thesis](https://amslaurea.unibo.it/id/eprint/25396)

## Tasks

The repository defines few tasks with the corresponding arenas:

- Collision avoidance
- Foraging
- T-maze

## Usage

Following, an example of use with the collision avoidance task and a E3O3A1 Tsetlin machine. The task is meant to run in background.

```
$ cp configurations/ca.json config.json                             # copy the default configuration for the task
$ cp machines/tsetlin-E3O3A.json tsetlin.json                       # copy the E3O3A1 Tsetlin machine
$ ./start_headless.sh main.py collision_avoidance-classic           # start the experiment in detached mode
$ mv config.json tsetlin.json ca                                    # move the configuration files to have a reference of the experiment details
$ git rev-parse HEAD > ca/git-hash                                  # save the hash of the currently used commit
$ git diff > ca/git-diffs                                           # save the differences from the commit
$ mkdir res                                                         # create a folder where to move the experiment data
$ mv ca res/$(date +%F-%H:%M)                                       # move the experiment data to the folder renaming it with the current time stamp (to avoid future collision)
```
