#!/bin/sh
# Create a fake desktop and open webots in it.
# It is possible to set up webots to run automatically,
# without human activation.

# define desktop environmental variables
export DEBIAN_FRONTEND=noninteractive
export DISPLAY=:99
export LIBGL_ALWAYS_SOFTWARE=true

# start a virtual screen with Xvfb
Xvfb :99 -screen 0 1024x768x16 &

# start webots
webots
