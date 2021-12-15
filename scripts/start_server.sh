#!/bin/sh
# Start the webots-server and check that all the folders exist.
# Finally, print the ports from which the session and simulation
# processes are listening.

cd /usr/local/webots/resources/web/server
mkdir -p log/session
chown $USER -R log
./server.sh stop default	
./server.sh start default &
sleep 1
echo 'PIDS'
ss -tulpn | grep LISTEN | grep python3 | awk -F ' ' '{print $5}' | awk -F ':' '{print $2}'

echo '
To start the simulation connect to: file:///usr/local/webots/resources/web/streaming_viewer/index.html
Connect to file in this way: ws://localhost:1999/session?url=file:///home/mandrab/Documents/hd_documents/uni/magistrale/tesi/learning-simulation/worlds/main_world.wbt
'

