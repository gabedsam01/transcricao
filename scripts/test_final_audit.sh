#!/bin/bash
set -e

mkdir -p tmp-tests output-tests
API_URL="http://127.0.0.1:8000"

# Find the main uvicorn process (or workers) using app.main
get_memory() {
  PIDS=$(pgrep -f "python -m app.main" || echo "")
  if [ -z "$PIDS" ]; then
    echo "0 MB"
    return
  fi
  TOTAL_RSS=0
  for pid in $PIDS; do
    # Get RSS in KB from ps
    rss_kb=$(ps -o rss= -p "$pid" | awk '{print $1}')
    if [ -n "$rss_kb" ]; then
      TOTAL_RSS=$((TOTAL_RSS + rss_kb))
    fi
  done
  # Convert to MB
  echo "$((TOTAL_RSS / 1024)) MB"
}

echo "Initial Memory before API (Should be 0): $(get_memory)"

# Download audio
if [ ! -f tmp-tests/horse.ogg ]; then
  curl -s -L -o tmp-tests/horse.ogg https://www.w3schools.com/html/horse.ogg
fi

# We assume API is running in background.
echo "Memory at IDLE (After startup/warmup): $(get_memory)"

# Health
echo ""
echo "--- Health Check ---"
curl -s $API_URL/health | jq .
echo "Memory after Health: $(get_memory)"

# Transcribe requests
for i in {1..3}; do
  echo ""
  echo "--- Request $i ---"
  START_TIME=$(date +%s.%N)
  curl -s -X POST -F "file=@tmp-tests/horse.ogg;type=audio/ogg" $API_URL/transcribe > output-tests/horse-$i.json
  END_TIME=$(date +%s.%N)
  DURATION=$(echo "$END_TIME - $START_TIME" | bc)
  
  echo "Transcribe status:"
  cat output-tests/horse-$i.json | jq '{text: .text, language: .language, duration: .duration}'
  
  echo "Time taken (curl real time): ${DURATION}s"
  echo "Memory after Request $i: $(get_memory)"
done

echo ""
echo "--- TMP Directory Cleanup ---"
ls -lh /tmp | grep tmp || echo "No left over tmp files found."
