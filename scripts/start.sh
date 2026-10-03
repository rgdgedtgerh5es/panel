#!/bin/sh
set -eu

# 3X-UI is the VPN management/backend service.
# The public web dashboard is served by the same container.
x-ui >/tmp/x-ui.log 2>&1 &

# Wait briefly for the local 3X-UI API.
i=0
while [ "$i" -lt 45 ]; do
  if wget -q -O /dev/null "http://127.0.0.1:2053/" 2>/dev/null; then
    break
  fi
  i=$((i+1))
  sleep 1
done

exec python3 /opt/vpnstan/web/server.py
