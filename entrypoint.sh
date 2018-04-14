#!/usr/bin/env bash
set -e

if [ "$1" == "start" ]; then
    python3 -m arbitrage -v -d -p${PROFIT:-20}
else
    exec "$@"
fi

