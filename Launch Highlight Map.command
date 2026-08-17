#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

PORT=8765
while lsof -i TCP:$PORT >/dev/null 2>&1; do
  PORT=$((PORT + 1))
done

python3 -m http.server $PORT &
SERVER_PID=$!
sleep 1
open "http://localhost:$PORT/Gopuff_Map_Local_Highlight.html"

echo "Map running at: http://localhost:$PORT/Gopuff_Map_Local_Highlight.html"
echo "Close this window to stop the server."

cleanup() {
  python3 -c "import os, signal; os.kill($SERVER_PID, signal.SIGTERM)" 2>/dev/null
  echo "Server stopped."
}
trap cleanup EXIT INT TERM
wait $SERVER_PID
