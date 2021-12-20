#!/bin/sh
# Create a fake desktop, setup a virtual environment and open webots simulation
# in it.

################################################################################
# DISPLAY HELP

if [[ $1 == '-h' ]]; then
  echo '
    Create a fake desktop, setup a virtual environment and open webots
    simulation in it.

    Synopsys:
      /path/to/start_headless.sh -h | MAIN_FILE.py
  '
  exit
fi

################################################################################
# DESKTOP SETUP

# define desktop environmental variables
export DEBIAN_FRONTEND=noninteractive
export DISPLAY=:99
export LIBGL_ALWAYS_SOFTWARE=true

# start a virtual screen with Xvfb
Xvfb :99 -screen 0 1024x768x16 > log 2>&1 &

################################################################################
# VIRTUAL ENVIRONMENT SETUP

# start virtual environment (and create if it does not exists)
if [[ ! -d venv ]]; then
  python3 -m venv venv
fi
source venv/bin/activate

# install pip requirements
pip install -r requirements.txt >> log 2>&1

################################################################################
# SIMULATION START

printf "\n\n\n" >> log
echo "Starting '$*' simulation" | tee -a log

# start webots simulation from .py specified file (in background)
python $* >>log 2>&1 &
