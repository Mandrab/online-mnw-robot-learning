#!/bin/sh
# Generate a partial template of the runned simulation

# get fields from configs
SEED=`cat controllers/runner/config/simulation.py | grep -F 'random.seed' | awk -F '(' '{print$2}' | awk -F ')' '{print$1}'`
REPLICA=`cat controllers/runner/config/simulation.py | grep -F 'replica_count =' | awk -F '= ' '{print $2}'`
EPOCHS=`cat controllers/runner/config/simulation.py | grep -F 'epoch_count =' | awk -F '= ' '{print $2}'`
DURATION=`cat controllers/runner/config/simulation.py | grep -F 'epoch_duration =' | awk -F '= ' '{print $2}'`

# get other fields
FREQUENCY=`cat controllers/runner/robot/epuck.py | grep -F 'Frequency(' | awk -F 'hz_value=|)' '{print $2}'`
LOAD=`cat controllers/runner/robot/epuck.py | grep -F 'actuators_load=' | awk -F '=|  # MOhm' '{print $2}'`
SIZE=`cat controllers/runner/optimization/utils.py | grep -F 'DEVICE_SIZE =' | awk -F '= ' '{print $2}'`
LENGTH=`cat controllers/runner/optimization/utils.py | grep -F 'WIRES_LENGTH =' | awk -F '= ' '{print $2}'`

# create readme file
touch README.md
echo "
EXECUTIONS RESULTS 
Date: 
Start time: 
End time: 
--------------------------------------------------------------------------------
Configuration:
    - random seed: $SEED
    - replicas: $REPLICA
    - epoch count: $EPOCHS
    - epoch duration: $DURATION
    - densities:
    - epuck freq: $FREQUENCY Hz
    - sensors range:
    - motor range:
    - network range: [0.0, 10.0]
    - device size: $SIZE
    - mean wires length: $LENGTH
    - std length: 0.35 * $LENGTH
    - actuators resistance: $LOAD
--------------------------------------------------------------------------------
`cat $1 | grep '^[fitness|Effective]'`
" #| tee README.md

