#!/bin/sh
# Generate a partial template of the run simulation

# configurations files
CONFIGS=`cat controllers/runner/config/simulation.py`
ROBOT=`cat controllers/runner/robot/epuck.py`
UTILS=`cat controllers/runner/optimization/utils.py`

# get fields from configs
DURATION=`cat <<<$CONFIGS | awk -F 'epoch_duration =' '$2{print $2}'`
EPOCHS=`cat <<<$CONFIGS | awk -F 'epoch_count = ' '$2{print $2}'`
FITNESS=`cat <<<$CONFIGS | awk -F 'MINIMUM_FITNESS = ' '$2{print $2}'`
LOAD=`cat <<<$CONFIGS | awk -F 'robot.motors_load = ' '$2{print $2}'`
REPLICA=`cat <<<$CONFIGS | awk -F 'replica_count = ' '$2{print $2}'`
SEED=`echo $CONFIGS | grep -F 'random.seed' | awk -F '[()]' '$2{print$2}'`
TASK=`cat <<<$CONFIGS | awk -F 'task = Tasks.' '$2{print $2}'`

# get other fields
FREQUENCY=`cat <<<$ROBOT | grep -F 'Frequency(' | awk -F 'hz_value=|)' '{print $2}'`
LENGTH=`cat <<<$UTILS | awk -F 'WIRES_LENGTH = ' '$2{print $2}'`
SIZE=`cat <<<$UTILS | awk -F 'DEVICE_SIZE = ' '$2{print $2}'`

# data from log file
START_DATE=`cat $1 | grep -F '[' | head -n 1 | awk -F '[|[[:space:]]' '{print $2}'`
START_TIME=`cat $1 | grep -F '[' | head -n 1 | awk '{print $2}'`
END_DATE=`cat $1 | grep -F '[' | tail -n 1 | awk -F '[|[[:space:]]' '{print $2}'`
END_TIME=`cat $1 | grep -F '[' | tail -n 1 | awk '{print $2}'`
WORLD_FILE=`cat $1 | grep 'Running simulation in' | awk -F ' ' '{print $4}'`

# create readme file
echo "
EXECUTIONS RESULTS
Date: [$START_DATE, $END_DATE]
Start time: $START_TIME
End time: $END_TIME
--------------------------------------------------------------------------------
Configuration:
    1. task and world:
      - random seed: $SEED
      - world: $WORLD_FILE
      - task: $TASK
    2. optimization:
      - replicas: $REPLICA
      - epoch count: $EPOCHS
      - epoch duration: $DURATION
      - densities:
      - minimum fitness to evolve: $FITNESS
    3. robot characteristics:
      - epuck freq: $FREQUENCY Hz
      - sensors range:
      - motor range:
      - actuators resistance: $LOAD
    4. network:
      - network range: [0.0, 10.0]
      - device size: $SIZE
      - mean wires length: $LENGTH
      - std length: 0.35 * $LENGTH
    5. others:
    - git-head hash: `git rev-parse HEAD`
--------------------------------------------------------------------------------
`cat $1 | grep '^[fitness|Creation]'`
"
