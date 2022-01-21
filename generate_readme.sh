#!/bin/bash
# Generate a partial template of the run simulation

# configurations files
CONFIGS=$(cat controllers/runner/config.py)
ROBOT=$(cat controllers/runner/robot/body.py)
UTILS=$(cat controllers/runner/optimization/utils.py)

# get fields from configs
DURATION=$(cat <<<"$CONFIGS" | awk -F 'epoch_duration = ' '$2{print $2}')
EPOCHS=$(cat <<<"$CONFIGS" | awk -F 'epoch_count = ' '$2{print $2}')
FITNESS=$(cat <<<"$CONFIGS" | awk -F 'evolution_threshold = ' '$2{print $2}')
REPLICA=$(cat <<<"$CONFIGS" | awk -F 'replica_count = ' '$2{print $2}')
SEED=$(echo "$CONFIGS" | awk -F 'random.seed[(]' '$2{sub(")", ""); print $2}')
TASK=$(cat <<<"$CONFIGS" | awk -F 'task: Tasks = Tasks.' '$2{print $2}')

# get other fields
FREQUENCY=$(cat <<<"$ROBOT" | awk -F 'hz_value=' '$2{sub(")", ""); print $2}')
LENGTH=$(cat <<<"$UTILS" | awk -F 'WIRES_LENGTH = ' '$2{print $2}')
SIZE=$(cat <<<"$UTILS" | awk -F 'DEVICE_SIZE = ' '$2{print $2}')
GIT_HASH=$(git rev-parse HEAD)

# data from log file
START_DATE=$(grep -F '[' "$1" | head -n 1 | awk -F '[|[[:space:]]' '{print $2}')
START_TIME=$(grep -F '[' "$1" | head -n 1 | awk '{print $2}')
END_DATE=$(grep -F '[' "$1" | tail -n 1 | awk -F '[|[[:space:]]' '{print $2}')
END_TIME=$(grep -F '[' "$1" | tail -n 1 | awk '{print $2}')
DENSITIES=$(awk -F 'densities: ' '$2{print $2}' < "$1")
LOADS=$(awk -F 'loads: ' '$2{print $2}' < "$1")

# create readme file
echo "\
EXECUTIONS RESULTS
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
      - sensors range:
      - motor range:
      - actuators resistances: $LOADS
    4. network:
      - network range: [0.0, 10.0]
      - device size: $SIZE
      - mean wires length: $LENGTH
      - std length: 0.35 * $LENGTH
    5. others:
      - git-head hash: $GIT_HASH
--------------------------------------------------------------------------------
$(grep '[fitness|Creation]' "$1" | awk -F '   ' '$2{print$2}')
"
