#!/usr/bin/env bash
set -e

cd ~/arbiter/

if [ "$1" == "start" ]; then
    git pull
    python3 -m arbitrage -v -d -p${PROFIT:-20}
else
    exec "$@"
fi

