#!/bin/bash
# Generate a partial template of the run simulation

# configurations files
CONFIGS="controllers/runner/config.py"
ROBOT="controllers/runner/robot/body.py"
UTILS="controllers/runner/optimization/utils.py"

# get fields from configs
DURATION=$(awk -F 'epoch_duration = ' '$2{print $2}' $CONFIGS)
EPOCHS=$(awk -F 'epoch_count = ' '$2{print $2}' $CONFIGS)
FITNESS=$(awk -F 'evolution_threshold = ' '$2{print $2}'  $CONFIGS)
REPLICA=$(awk -F 'replica_count = ' '$2{print $2}' $CONFIGS)
SEED=$(awk -F 'random.seed[(]' '$2{sub(")", ""); print $2}' $CONFIGS)
TASK=$(awk -F 'task: Tasks = Tasks.' '$2{print $2}' $CONFIGS)

# get other fields
FREQUENCY=$(awk -F 'hz_value=' '$2{sub(")", ""); print $2}' $ROBOT)
LENGTH=$(awk -F 'WIRES_LENGTH = ' '$2{print $2}' $UTILS)
SIZE=$(awk -F 'DEVICE_SIZE = ' '$2{print $2}' $UTILS)
GIT_HASH=$(git rev-parse HEAD)

# data from log file
START_DATE=$(grep -F '[' "$1" | head -n 1 | awk -F '[|[[:space:]]' '{print $2}')
START_TIME=$(grep -F '[' "$1" | head -n 1 | awk '{print $2}')
END_DATE=$(grep -F '[' "$1" | tail -n 1 | awk -F '[|[[:space:]]' '{print $2}')
END_TIME=$(grep -F '[' "$1" | tail -n 1 | awk '{print $2}')
DENSITIES=$(awk -F 'densities: ' '$2{print $2}' "$1")
LOADS=$(awk -F 'loads: ' '$2{print $2}' "$1")

# create readme file
echo "\
**EXECUTIONS RESULTS**
Date: [$START_DATE, $END_DATE]
Start time: $START_TIME
End time: $END_TIME
--------------------------------------------------------------------------------
Configuration:
  1. task and world:
      - random seed: $SEED
      - world:
      - task: $TASK
  2. optimization:
      - replicas: $REPLICA
      - epoch count: $EPOCHS
      - epoch duration: $DURATION
      - densities: $DENSITIES
      - minimum fitness to evolve: $FITNESS
  3. robot characteristics:
      - epuck freq: $FREQUENCY Hz
      - actuators resistances: $LOADS
  4. network:
      - network range: [0.0, 10.0]
      - device size: $SIZE
      - mean wires length: $LENGTH
      - std length: 0.35 * $LENGTH
  5. others:
      - git-head hash: $GIT_HASH
--------------------------------------------------------------------------------
$(grep '[fitness|Creation]' "$1" | awk -F '\\][ |\t]+' '$2{print$2}  ')
" | awk '{print $0"  "}'
